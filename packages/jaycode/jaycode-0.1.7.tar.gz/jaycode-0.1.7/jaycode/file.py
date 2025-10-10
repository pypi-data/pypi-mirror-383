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
