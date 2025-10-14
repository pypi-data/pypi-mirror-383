import subprocess
import os

class FileNamespace:
    def __init__(self, parent):
        self.parent = parent

    def m4a_to_wav(self, m4a_path: str, wav_path: str, ffmpeg_path: str = r"C:\ffmpeg\bin\ffmpeg.exe"):
        """
        ffmpeg 실행 파일을 직접 지정해서 m4a → wav 변환
        https://www.gyan.dev/ffmpeg/builds/ exe 파일 설치 필수
        """

        if not os.path.isfile(ffmpeg_path):
            raise FileNotFoundError(f"[ffmpeg] 실행 파일을 찾을 수 없습니다: {ffmpeg_path}")

        # m4a 절대경로
        m4a_abs = os.path.abspath(m4a_path)

        # wav_path가 디렉토리 없이 파일명만 있다면 → m4a_path와 같은 폴더로 설정
        if not os.path.dirname(wav_path):
            m4a_dir = os.path.dirname(m4a_abs)
            wav_path = os.path.join(m4a_dir, wav_path)

        wav_abs = os.path.abspath(wav_path)

        try:
            subprocess.run(
                [ffmpeg_path, "-y", "-i", m4a_abs, wav_abs],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"[ffmpeg] 변환 완료: {wav_abs}")
            return wav_abs
        except subprocess.CalledProcessError as e:
            raise Exception(f"[ffmpeg] ❌ 변환 실패: {e.stderr.decode()}")

    def delete_file(self,path: str):
        """
        지정된 경로의 파일을 삭제합니다.
        파일이 존재하지 않거나 접근 권한이 없을 경우 예외를 발생시킵니다.

        Args:
            path (str): 삭제할 파일의 경로

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
            PermissionError: 파일이 사용 중이거나 권한이 없을 때
            IsADirectoryError: 경로가 폴더일 때
            Exception: 기타 예외
        """
        # 경로가 존재하지 않음
        if not os.path.exists(path):
            raise FileNotFoundError(f"파일이 존재하지 않습니다: {path}")

        # 폴더인 경우
        if os.path.isdir(path):
            raise IsADirectoryError(f"지정된 경로는 파일이 아니라 폴더입니다: {path}")

        # 삭제 시도
        try:
            os.remove(path)
        except PermissionError:
            raise PermissionError(f"파일이 사용 중이거나 권한이 없습니다: {path}")
        except Exception as e:
            raise Exception(f"파일 삭제 중 오류 발생: {e}")
