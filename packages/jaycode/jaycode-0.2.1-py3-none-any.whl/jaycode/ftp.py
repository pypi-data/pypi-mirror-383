from ftplib import FTP,error_perm
import os
import platform

def check_connection(func):
    def wrapper(self,*args, **kwargs):
        if not self.connected:
            raise RuntimeError("FTP 연결이 필요합니다.")
        return func(self, *args, **kwargs)

    return wrapper

class FTPNamespace:
    """[FTP] 관련 기능 모음"""
    connected = False

    def __init__(self,parent):
        self.parent = parent

    def connect(self,host, user,passwd,port=21):
        try:
            self.ftp = FTP()
            self.ftp.connect(host,port=port)
            self.ftp.login(user=user, passwd=passwd)

            # ✅ 서버 OS 감지 (SYST 명령)
            try:
                system_info = self.ftp.sendcmd("SYST").lower()
                if "windows" in system_info:
                    self.ftp.encoding = "cp949"
                else:
                    self.ftp.encoding = "utf-8"
                print(f"[FTP] 서버 OS 감지: {system_info} → 인코딩 설정: {self.ftp.encoding}")
            except Exception as e:
                # 감지 실패 시 기본값
                self.ftp.encoding = "utf-8"
                print(f"[FTP] 서버 OS 감지 실패. 기본 인코딩 적용: {self.ftp.encoding} ({e})")


            print(f"[FTP] 연결 성공: {host}@{user}")
            self.connected = True
        except Exception as e:
            self.connected = False
            raise ValueError(f"[FTP] 연결 실패: {e}")

    @check_connection
    def ls(self):
        self.ftp.nlst()

    @check_connection
    def get_file(self, remote_path, local_path: str = "", name: str = ""):
        """
        FTP로 원격 파일을 다운로드하여 로컬에 저장하고 저장경로 반환.
        remote_path : 원격 파일 전체 경로 (예: /home/user/file.m4a)
        local_path  : 로컬 폴더(디렉토리) 경로. 지정하지 않으면 ./remote_files 사용
        name        : 저장할 파일명(확장자 포함 또는 제외). 비어있으면 원본 이름 사용
        """
        try:
            # 로컬 기본 폴더 처리
            if not local_path:
                base_dir = os.getcwd()
                local_path = os.path.join(base_dir, "remote_files")
            os.makedirs(local_path, exist_ok=True)

            original_name = os.path.basename(remote_path)
            original_ext = os.path.splitext(original_name)[1]

            # 저장할 파일명 결정
            if not name:
                filename = original_name
            else:
                # name에 확장자가 없으면 원본 확장자 붙임
                if os.path.splitext(name)[1] == "":
                    filename = f"{name}{original_ext}"
                else:
                    filename = name

            save_path = os.path.join(local_path, filename)

            ftp = self.ftp  # ftplib.FTP 인스턴스
            try:
                ftp.set_pasv(True)
            except Exception:
                pass

            # 원격 파일 존재 확인 (서버가 SIZE 지원하지 않을 수 있으므로 두 방식 시도)
            exists = False
            try:
                # SIZE가 지원되면 파일 크기를 얻어 존재 확인
                ftp.size(remote_path)
                exists = True
            except Exception:
                # SIZE 실패 시 부모 디렉토리의 목록에서 파일명 검색
                try:
                    dirpath = os.path.dirname(remote_path) or "."
                    basename = os.path.basename(remote_path)
                    listing = ftp.nlst(dirpath)
                    names = [os.path.basename(x.rstrip("/")) for x in listing]
                    if basename in names:
                        exists = True
                except Exception:
                    exists = False

            if not exists:
                raise Exception(f"[FTP] ❌ 원격 파일이 존재하지 않습니다: {remote_path}")
                return None

            # 다운로드
            with open(save_path, "wb") as f:
                ftp.retrbinary(f"RETR {remote_path}", f.write, blocksize=8192)

            print(f"[FTP] 파일 다운로드 성공: {remote_path} → {save_path}")
            return save_path

        except error_perm as e:
            # 권한 또는 파일 없음 등 서버 응답 관련 오류
            raise Exception(f"[FTP] ❌ 파일 다운로드 실패(서버 응답): {e}")
            return None
        except Exception as e:
            raise Exception(f"[FTP] ❌ 파일 다운로드 실패: {e}")
            return None

    @check_connection
    def upload_file(self, local_path: str, remote_path: str = "", name: str = ""):
        """
        FTP로 로컬 파일을 업로드합니다.
        local_path : 업로드할 로컬 파일 전체 경로
        remote_path: 원격 저장 디렉토리 경로. 비어있으면 루트("/")에 업로드 "/test/example" 시 /test/example/name 으로 들어감
        name       : 원격 저장 파일명. 비어있으면 원본 파일명 사용
        """
        try:
            if not os.path.isfile(local_path):
                raise Exception(f"[FTP] ❌ 로컬 파일이 존재하지 않습니다: {local_path}")

            original_name = os.path.basename(local_path)
            original_ext = os.path.splitext(original_name)[1]

            # 업로드 파일명 결정
            if not name:
                filename = original_name
            else:
                # name에 확장자가 없으면 원본 확장자 붙임
                if os.path.splitext(name)[1] == "":
                    filename = f"{name}{original_ext}"
                else:
                    filename = name

            # 최종 원격 경로 결정
            if not remote_path:
                remote_file = filename
            else:
                remote_file = os.path.join(remote_path, filename).replace("\\", "/")

            ftp = self.ftp
            try:
                ftp.set_pasv(True)
            except Exception:
                pass

            # ✅ (1) remote_path가 있다면 경로 생성
            if remote_path:
                dirs = remote_path.strip("/").split("/")
                current = ""
                for d in dirs:
                    current += f"/{d}"
                    try:
                        ftp.mkd(current)
                    except Exception:
                        pass  # 이미 있으면 무시

            # ✅ (2) 업로드 실행
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {remote_file}", f, blocksize=8192)

            print(f"[FTP] 파일 업로드 성공: {local_path} → {remote_file}")
            return remote_file

        except error_perm as e:
            raise Exception(f"[FTP] ❌ 파일 업로드 실패(서버 응답): {e}")
        except Exception as e:
            raise Exception(f"[FTP] ❌ 파일 업로드 실패: {e}")

    @check_connection
    def close(self):
        """
        FTP 연결을 종료합니다.
        """
        try:
            self.ftp.quit()  # 정상 종료 명령
            print("[FTP] 연결 종료 완료")
        except Exception as e:
            print(f"[FTP] 종료 중 오류 발생: {e}")
        finally:
            self.connected = False