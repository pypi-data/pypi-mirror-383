import paramiko
import os

def check_connection(func):
    def wrapper(self,*args, **kwargs):
        if not self.connected:
            raise RuntimeError("SSH 연결이 필요합니다.")
        return func(self, *args, **kwargs)

    return wrapper

class SSHNamespace:
    """[SSH] 관련 기능 모음"""
    connected = False

    def __init__(self,parent):
        self.parent = parent

    def connect(self,hostname,username,password,port=22):
        """
          [SSH] 서버에 연결합니다.

          Args:
              hostname (str): SSH 서버 주소 (예: example.com)
              username (str): 로그인 아이디
              password (str): 로그인 비밀번호
              port (int): 접속 포트 기본값 22
          """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

        try :
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname=self.hostname,username=self.username,password=self.password,port=self.port)
            self.connected = True
            print(f"[SSH] 연결 성공: {self.username}@{self.hostname}:{self.port}")

        except Exception as e:
            self.connected = False
            raise ValueError(f"[SSH] 연결 실패: {e}")

    @check_connection
    def get_file(self, remote_path, local_path: str = "", name: str = ""):
        try:
            # ✅ 기본 로컬 경로 설정
            if not local_path:
                base_dir = os.getcwd()
                local_path = os.path.join(base_dir, "remote_files")
                os.makedirs(local_path, exist_ok=True)

            original_name = os.path.basename(remote_path)
            original_ext = os.path.splitext(original_name)[1]

            if not name:
                filename = original_name
            else:
                if os.path.splitext(name)[1] == "":
                    filename = f"{name}{original_ext}"
                else:
                    filename = name

            save_path = os.path.join(local_path, filename)

            # ✅ 다운로드
            sftp = self.ssh.open_sftp()

            # 원격 파일 존재 확인
            try:
                sftp.stat(remote_path)
            except FileNotFoundError:
                raise Exception(f"[SSH] ❌ 원격 파일이 존재하지 않습니다: {remote_path}")

            sftp.get(remote_path, save_path)
            sftp.close()

            print(f"[SSH] 파일 다운로드 성공: {remote_path} → {save_path}")
            return save_path

        except Exception as e:
            raise Exception(f"[SSH] ❌ 파일 다운로드 실패: {e}")
