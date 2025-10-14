from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import types

from selenium.webdriver.common.by import By
import atexit

def check_init(func):
    def wrapper(self,*args, **kwargs):
        if not self.initd:
            raise RuntimeError("초기화 설정이 필요합니다.")
        return func(self, *args, **kwargs)

    return wrapper

class CrawlingNamespace:
    driver = None
    initd = False

    def __init__(self, parent):
        self.parent = parent

    def init(self, headless: bool = False, secret: bool = False,
             window_size: str = "800,600", auto_quit: bool = True,
             fast: bool = True, cache: str = None, user_agent: str = None):
        """
        Selenium 브라우저 초기화 클래스
        Args:
            headless (bool): True → 백그라운드 실행(창 안뜸), False → 일반 모드
            secret (bool): True → 시크릿 모드
            window_size (str): 브라우저 창 크기 (기본 800x600)
            auto_quit (bool): True → 파이썬 종료 시 브라우저 자동 종료
            fast (bool): True → 이미지 로딩 비활성화 (빠른 실행)
            cache (str): 캐시 폴더 경로 (예: 'c:/cache/user1')
            user_agent (str): 사용자 정의 User-Agent
        """
        options = Options()
        options.add_argument(f"--window-size={window_size}")
        options.add_argument("--disable-features=ChromeWhatsNewUI")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # headless 모드
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        # 시크릿 모드
        if secret:
            options.add_argument("--incognito")

        # 빠른 모드 (이미지 로딩 차단)
        if fast:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)

        # 캐시 폴더 지정
        if cache:
            options.add_argument(f"--user-data-dir={cache}")
            options.add_argument(f"--disk-cache-dir={cache}")

        # User-Agent 지정
        if user_agent:
            options.add_argument(f"user-agent={user_agent}")

        options.add_experimental_option("detach", True)

        # 브라우저 실행
        self.driver = webdriver.Chrome(options=options)
        self.initd = True

        if auto_quit:
            atexit.register(self.quit)

    @check_init
    def open(self, url):
        self.driver.get(url)

    @check_init
    def quit(self):
        self.driver.quit()

    @check_init
    def find(self, selector: str,
             by: str = "auto",
             mode: str = "element",
             timeout: int = 2,
             index: int = 0,
             text_search: bool = False,
             clickable: bool = False,
             el=None):
        """
        범용 element 탐색 함수
        Args:
            selector (str): 검색어 (id/class/css/xpath/text)
            by (str): 'id' | 'class' | 'css' | 'xpath' | 'auto'
            mode (str): 'element' | 'elements' | 'text'
            timeout (int): 최대 대기 시간
            index (int): 여러 개 중 몇 번째 선택할지 (mode='element'일 때만 적용)
            text_search (bool): 텍스트 포함 검색 허용 여부
            clickable (bool): 클릭 가능한 상태까지 기다릴지 여부
            el (WebElement): 특정 element 하위에서만 검색할 때 지정
        Returns:
            element / [elements] / [text...]
        """
        driver = self.driver
        wait = WebDriverWait(driver, timeout)

        # 검색 context
        context = el if el is not None else driver

        # 검색 전략 정의
        strategies = []
        if by == "id":
            strategies = [(By.ID, selector)]
        elif by == "name":
            strategies = [(By.NAME, selector)]
        elif by == "tag":
            strategies = [(By.TAG_NAME, selector)]
        elif by == "class":
            strategies = [(By.CLASS_NAME, selector)]
        elif by == "css":
            strategies = [(By.CSS_SELECTOR, selector)]
        elif by == "xpath":
            strategies = [(By.XPATH, selector)]
        elif by == "auto":
            strategies = [
                (By.ID, selector),
                (By.NAME, selector),
                (By.TAG_NAME, selector),
                (By.CLASS_NAME, selector),
                (By.CSS_SELECTOR, selector),
            ]
            if text_search:
                strategies.append(
                    (By.XPATH,
                     f"//*[not(self::script or self::style or self::meta or self::link) "
                     f"and contains(normalize-space(text()), '{selector}')]")
                )

        # 전략 실행
        for by, value in strategies:
            try:
                # wait.until 은 driver 전역 검색에만 적용
                if el is None:
                    condition = None
                    if mode == "elements":
                        condition = EC.presence_of_all_elements_located((by, value))
                    else:
                        condition = EC.presence_of_element_located((by, value))

                    if clickable:
                        condition = EC.element_to_be_clickable((by, value))

                    wait.until(condition)

                # elements 모드
                if mode == "elements":
                    elements = context.find_elements(by, value)
                    return [e for e in elements
                            if e.tag_name.lower() not in ["script", "style", "meta", "link"]]

                # element 모드
                if mode == "element":
                    elements = context.find_elements(by, value)
                    clean = [e for e in elements
                             if e.tag_name.lower() not in ["script", "style", "meta", "link"]]
                    if not clean:
                        return None

                    el = clean[index] if index < len(clean) else clean[0]
                    el.control = types.MethodType(self.control, el)

                    return el

                # text 모드
                if mode == "text":
                    elements = context.find_elements(by, value)
                    texts = []
                    for e in elements:
                        texts.append(self.text(e))  # self.text() 사용
                    return texts

            except (TimeoutException, StaleElementReferenceException):
                continue

        return [] if mode in ("elements", "text") else None

    def text(self,el):
        if el.tag_name.lower() in ["script", "style", "meta", "link"]:
            return []
        if el.tag_name.lower() == "tr":
            tds = el.find_elements(By.TAG_NAME, "td")
            return [td.text.strip() for td in tds]

        else:
            return [t.strip() for t in el.text.split("\n") if t.strip()]

    @check_init
    def tab(self, url: str = "about:blank",timeout: int = 10):
        """
        특정 URL을 포함한 탭으로 전환.
        - 이미 열려 있으면 해당 탭으로 전환
        - 없으면 새 탭 열고 해당 URL 로딩 후 전환
        Args:
            url (str): 전환하거나 열고 싶은 URL
        Returns:
            True (성공)
        """
        driver = self.driver

        # 이미 열린 탭들 검사
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if url in driver.current_url:
                return True

        # 없다면 새 탭 열기
        driver.execute_script(f"window.open('{url}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        # 페이지 로드 안정화 대기
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

        except Exception:
            raise "[Crawling] 구글 탭 로딩 실패"


    @check_init
    def control(self, el, value=None):
        """
        WebElement 또는 WebElement 리스트를 받아 자동 제어
        - input/textarea/select → 단일 element
        - checkbox/radio → els(리스트)로 받아 value 매칭 처리
        """
        if el is None:
            raise ValueError("요소가 None 입니다.")

        # 여러 개 elements가 넘어온 경우
        if isinstance(el, list) and len(el) > 0:
            tag = el[0].tag_name.lower()
            input_type = (el[0].get_attribute("type") or "").lower()

            # 체크박스 그룹
            if input_type == "checkbox":
                for cb in el:
                    if value is None or cb.get_attribute("value") == str(value):
                        cb.click()  # 토글
                        return cb
                raise ValueError(f"체크박스 그룹에서 '{value}' 찾을 수 없음")

            # 라디오 그룹
            if input_type == "radio":
                for r in el:
                    if r.get_attribute("value") == str(value):
                        if not r.is_selected():
                            r.click()
                        return r
                raise ValueError(f"라디오 그룹에서 '{value}' 찾을 수 없음")

            raise TypeError("els는 checkbox 또는 radio만 지원합니다.")

        # 단일 element
        tag = el.tag_name.lower()
        input_type = (el.get_attribute("type") or "").lower()

        if str(value).lower() == "click":
            self.click(el)
            return el

        if tag in ["input", "textarea"]:
            if input_type in ["text", "password", "email", "number", ""] or tag == "textarea":
                self.driver.execute_script("""
                            arguments[0].value = arguments[1];
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        """, el, str(value))

            elif input_type == "date":
                date_str = str(value)  # 예: "2025-10-02"
                self.driver.execute_script("""
                        arguments[0].value = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """, el, date_str)
            else:
                raise TypeError(f"단일 el은 텍스트 입력만 지원합니다. type={input_type}")

        elif tag == "select":
            Select(el).select_by_visible_text(str(value))

        else:
            raise TypeError(f"지원되지 않는 태그: <{tag}>")

        return el

    @check_init
    def click(self, el, timeout: int = 5, stable_time: float = 0.5):
        """
        클릭 후 이벤트가 '끝난 느낌'이 날 때까지 대기
        """
        driver = self.driver

        # 안전하게 클릭 시도
        try:
            el.click()
        except Exception:
            # 기본 클릭이 안되면 JS 클릭으로 fallback
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", el)

        end_time = time.time() + timeout
        last_source = None
        stable_start = None

        while time.time() < end_time:
            try:
                ready = driver.execute_script("return document.readyState")
                if ready != "complete":
                    stable_start = None
                    continue

                try:
                    active = driver.execute_script("return window.jQuery ? jQuery.active : 0")
                except Exception:
                    active = 0

                if active > 0:
                    stable_start = None
                    continue

                source = driver.page_source
                if source == last_source:
                    if stable_start is None:
                        stable_start = time.time()
                    elif time.time() - stable_start >= stable_time:
                        return True
                else:
                    stable_start = None
                last_source = source

                time.sleep(0.1)

            except Exception:
                stable_start = None
                time.sleep(0.1)

        return False