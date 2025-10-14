# jaycode
[![PyPI version](https://img.shields.io/pypi/v/jaycode.svg)](https://pypi.org/project/jaycode/)
[![Downloads](https://img.shields.io/pypi/dm/jaycode.svg)](https://pypi.org/project/jaycode/)

`jaycode` 는 SSH, FTP, DB, File, Crawling 관련 작업을 쉽게 할 수 있는 파이썬 유틸리티 패키지입니다.  

---

## 📦 설치 (Installation)

```bash 
pip install jaycode
```

## 🚀 사용 예시 (Examples)
```
import jaycode

exam = jaycode.Core()

exam.SSH.connect(hostname=,username=,password=)

exam.FTP.connect(host=,user=,passwd=)

exam.DB.connect(user=,password=,database=)
exam.DB.insert(dict,'table_name')

exam.Crawling.init()
exam.Crawling.open('https://naver.com')
exam.Crawling.find('exam',"id",mode="element").control('data or click')
```

## 🌲 구조도 (Tree 구조)

- jaycode
  - **ssh**
    - `connect()` ssh 연결함수
    - `get_file()` 연결된 서버에서 파일 가져오는 함수
  - **ftp**
    - `connect()` ftp 연결함수
    - `get_file()` 연결된 서버에서 파일 가져오는 함수
    - `upload_file()` 연결된 서버에 파일 업로드 함수
  - **db**
    - `connect()` db 연결함수
    - `insert()` 데이터 추가함수
    - `update()` 데이터 수정함수
    - `delete()` 데이터 삭제함수
    - `query()` 쿼리함수
  - **file**
    - `m4a_to_wav()` 파일 변환함수
  - **crawling**
      - `init()` 드라이버 초기화 함수
      - `open()` 페이지 오픈 함수
      - `quit()` 페이지 닫기 함수 
      - `find()` 엘리먼트를 찾는 함수
      - `text()` 엘리먼트의 텍스트값을 배열로 반환하는함수
      - `tab()` 탭을 만들거나 선택하는 함수
      - `control()` input 타입 컨트롤 하는 함수
      - `click()` 엘리먼트 클릭후 이벤트가 종료될떄까지 대기하는 함수