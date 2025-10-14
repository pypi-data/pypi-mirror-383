import paramiko
import pymysql
from sshtunnel import SSHTunnelForwarder


def check_connection(func):
    def wrapper(self,*args, **kwargs):
        if not self.connected:
            raise RuntimeError("DB 연결이 필요합니다.")
        return func(self, *args, **kwargs)

    return wrapper

class DBNamespace :
    """[DB] 관련 기능 모음"""
    connected = False
    database = None

    def __init__(self, parent):
        self.parent = parent

    @property
    def SSH(self):
        return self.parent.SSH

    def connect(self,user,password,database,host = '127.0.0.1',port = 3306,charset='utf8mb4'):
        """
                  [DB] 디비에 연결합니다. host 기준으로 연결 방식이 다릅니다

                  Args:
                      user (str): DB 사용자
                      password (str): DB 사용자 비밀번호
                      database (str): DB명
                      host (str): DB 접속 로컬이 아닐경우 SSH가아닌 외부접속으로 시도
                      port (int): 접속 포트 기본값 3306
                      charset (str): 디비 문자셋 utf8mb4
        """
        if host == "127.0.0.1" or host == "localhost":
            self.ssh_connect(user,password,database,host,port,charset)



    def ssh_connect(self,user,password,database,host = '127.0.0.1',port = 3306,charset='utf8mb4'):
        if not self.SSH.connected:
            raise RuntimeError("SSH 연결이 필요합니다.")

        try :
            self.tunnel = SSHTunnelForwarder(
                (self.SSH.hostname, self.SSH.port),
                ssh_username=self.SSH.username,
                ssh_password=self.SSH.password,
                remote_bind_address=(host, port)
            )

            self.tunnel.start()

            self.conn = pymysql.connect(
                host=host,
                port=self.tunnel.local_bind_port,
                user=user,
                password=password,
                database=database,
                charset=charset
            )
            self.connected = True

            self.database = database

            print(f"[DB] 연결 성공 {database}@{user}:{port}")
            self.load_tables()
        except Exception as e :
            self.connected = False
            print(e)

    @check_connection
    def query(self, sql):
        if not self.conn:
            raise RuntimeError("DB 연결이 필요합니다.")
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]  # 컬럼 이름 가져오기
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]  # 튜플 → dict
            return result

    @check_connection
    def load_tables(self):
        tables = []

        with self.conn.cursor() as cursor:
            # 1️⃣ 테이블 목록 조회
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = %s
            """, (self.database,))
            table_names = [row[0] for row in cursor.fetchall()]

            # 2️⃣ 각 테이블의 컬럼, PK, 타입 조회
            for tbl in table_names:
                cursor.execute("""
                    SELECT COLUMN_NAME, COLUMN_KEY, DATA_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """, (self.database, tbl))
                columns_data = cursor.fetchall()

                columns = [col[0] for col in columns_data]
                primary = next((col[0] for col in columns_data if col[1] == "PRI"), None)

                # ✅ 컬럼명 : 데이터타입 매핑
                columns_type = {col[0]: col[2] for col in columns_data}

                tables.append({
                    "table": tbl,
                    "columns": columns,
                    "primary": primary,
                    "columns_type": columns_type
                })

        self.tables = tables
        print(f"[DB] 테이블 로딩 완료")

    def is_table(self, table):
        if not hasattr(self, "tables") or not self.tables:
            raise RuntimeError("아직 테이블 정보가 로드되지 않았습니다. 먼저 load_tables()를 호출하세요.")

        for tbl in self.tables:
            if tbl["table"] == table:
                return tbl

            # 없으면 에러
        raise RuntimeError(f"테이블이 존재하지 않습니다: {table}")

    @check_connection
    def update(self, row, table=""):
        if not isinstance(row, dict):
            raise RuntimeError("row는 dict형태여야 합니다.")
        if "table" not in row and not table:
            raise RuntimeError("지정된 테이블이 없습니다.")

        table = table or row.get("table")
        table_info = self.is_table(table)

        primary = table_info["primary"]
        if not primary:
            raise RuntimeError(f"Primary Key가 지정되지 않은 테이블입니다: {table}")

        if primary not in row:
            raise RuntimeError(f"row 데이터에 Primary Key({primary}) 값이 없습니다.")

        valid_columns = set(table_info["columns"])
        columns_type = table_info.get("columns_type", {})  # ✅ 컬럼 타입

        set_parts = []
        values = []

        for col, val in row.items():
            if col in ("table", primary):
                continue
            if col not in valid_columns:
                continue

            # ✅ int 타입 컬럼일 때 문자열이면 콤마 제거
            if columns_type.get(col, "").lower() in ("int", "bigint", "smallint", "mediumint", "tinyint"):
                if isinstance(val, str):
                    val = val.replace(",", "")

            # ✅ now() 처리
            if isinstance(val, str) and val.lower() == "now()":
                set_parts.append(f"`{col}` = NOW()")
            else:
                set_parts.append(f"`{col}` = %s")
                values.append(val)

        where_clause = f"`{primary}` = %s"
        values.append(row[primary])

        sql = f"UPDATE `{table}` SET {', '.join(set_parts)} WHERE {where_clause}"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, values)
            self.conn.commit()

    @check_connection
    def insert(self, row, table=""):
        if not isinstance(row, dict):
            raise RuntimeError("row는 dict형태여야 합니다.")
        if "table" not in row and not table:
            raise RuntimeError("지정된 테이블이 없습니다.")

        table = table or row.get("table")
        table_info = self.is_table(table)

        valid_columns = set(table_info["columns"])
        columns_type = table_info.get("columns_type", {})  # ✅ 컬럼 타입 정보 가져오기

        columns = []
        placeholders = []
        values = []

        for col, val in row.items():
            if col not in valid_columns:  # 테이블에 없는 컬럼이면 무시
                continue

            if columns_type.get(col, "").lower() in ("int", "bigint", "smallint", "mediumint", "tinyint"):
                if isinstance(val, str):
                    val = val.replace(",", "")

            columns.append(f"`{col}`")
            if isinstance(val, str) and val.lower() == "now()":
                placeholders.append("NOW()")
            else:
                placeholders.append("%s")
                values.append(val)

        if "insert_date" in valid_columns and "insert_date" not in row:
            columns.append("`insert_date`")
            placeholders.append("NOW()")

        if not columns:
            raise RuntimeError("유효한 컬럼 데이터가 없습니다.")

        sql = f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, values)
            self.conn.commit()
            return cursor.lastrowid  # AUTO_INCREMENT ID 반환

    @check_connection
    def delete(self, row, table=""):
        if not isinstance(row, dict):
            raise RuntimeError("row는 dict형태여야 합니다.")
        if "table" not in row and not table:
            raise RuntimeError("지정된 테이블이 없습니다.")

        table = table or row.get("table")
        table_info = self.is_table(table)

        primary = table_info["primary"]
        if not primary:
            raise RuntimeError(f"Primary Key가 지정되지 않은 테이블입니다: {table}")

        if primary not in row:
            raise RuntimeError(f"row에 Primary Key({primary}) 값이 없습니다.")

        sql = f"DELETE FROM `{table}` WHERE `{primary}` = %s"
        values = (row[primary],)

        with self.conn.cursor() as cursor:
            cursor.execute(sql, values)
            affected = cursor.rowcount
            self.conn.commit()

        if affected == 0:
            raise RuntimeError(f"[DB] 삭제 실패: {table}.{primary}={row[primary]} (해당 행 없음)")

        return affected  # 삭제된 행 수 반환


