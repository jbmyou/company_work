import time
import random
import re
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


# -------------------------------
# 예외 정의
# -------------------------------
class ErrorMsg(Exception):
    """작업 중 발생한 오류 메시지"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


# -------------------------------
# Selenium 유틸 클래스
# -------------------------------
class SCourtDriver:
    def __init__(self, headless: bool = False, wait_time: int = 30):
        self.driver = None
        self.wait_long = None
        self.wait_mid = None
        self.wait_short = None
        self.headless = headless
        self.wait_time = wait_time
        
    # ---------------------------
    # 유틸 함수 (딜레이)
    # ---------------------------
    @staticmethod
    def lwt():
        time.sleep(2.5)

    @staticmethod
    def mwt():
        time.sleep(1)

    @staticmethod
    def swt():
        time.sleep(random.uniform(0.2, 0.5))


    # ---------------------------
    # 내부 드라이버 설정
    # ---------------------------
    def _set_chrome_driver(self, headless: bool) -> webdriver.Chrome:
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
        
    # ---------------------------
    # 사이트 접속 및 로그인
    # ---------------------------
    def connect(self, url: str = "https://ecfs.scourt.go.kr/psp/index.on", click_login: bool = True) -> None:
        # 드라이버가 없으면 생성
        if self.driver is None:
            self.driver = self._set_chrome_driver(self.headless)
            self.wait_long  = WebDriverWait(self.driver, 30)
            self.wait_mid   = WebDriverWait(self.driver, 10)
            self.wait_short = WebDriverWait(self.driver, 3)
        
        self.driver.get(url)
        self.driver.maximize_window()
        
        if click_login:
            self.wait_long.until(
                EC.element_to_be_clickable((By.ID, 'mf_pmf_content1_btnMainLogin'))
            ).click()
            self.mwt()


    def login_with_cert(self, user_id: str, cert_name: str, cert_key: str) -> None:
        """아이디 로그인 후 인증서 로그인 수행"""
        # 아이디 입력
        input_id = self.wait_short.until(
            EC.element_to_be_clickable((By.ID, "mf_pfwork_ibx_elpUserIdForCert"))
        )
        input_id.send_keys(user_id)
        self.swt()

        # 로그인 버튼 클릭
        login_btn = self.wait_short.until(
            EC.element_to_be_clickable((By.ID, "mf_pfwork_btn_certlogin"))
        )
        login_btn.click()
        self.mwt()

        # 인증서 입력
        self._certify(cert_name, cert_key)

    def _certify(self, cert_name: str, cert_key: str) -> None:
        """인증서 선택 및 비밀번호 입력"""
        self.lwt()
        try:
            cert_elem_xpath = f'//*[@id="xwup_cert_table"]/table/tbody/tr/td/div[text()="{cert_name}"]'
            cert_elem = self.wait_long.until(
                EC.element_to_be_clickable((By.XPATH, cert_elem_xpath))
            )
            cert_elem.click()
            self.swt()

            input_key = self.wait_mid.until(
                EC.element_to_be_clickable((By.ID, "xwup_certselect_tek_input1"))
            )
            input_key.send_keys(cert_key)
            self.swt()

            ok_btn = self.wait_short.until(
                EC.element_to_be_clickable((By.ID, "xwup_OkButton"))
            )
            ok_btn.click()
            self.mwt()
        except TimeoutException as e:
            raise ErrorMsg(f"인증서 선택 또는 입력 실패: {e}")


    # ---------------------------
    # 오류 처리
    # ---------------------------
    def check_error_popup(self) -> Optional[str]:
        """작업 대상이 아닌 알람 발생 시 확인 버튼 누르고 메시지 반환"""
        popups = self.driver.find_elements(By.CLASS_NAME, "w2popup_window")
        if not popups:
            return None
        popup_msg = popups[0].find_element(By.CLASS_NAME, "w2textbox").text
        try:
            confirm_btn = self.wait_short.until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'confirm'))
            )
            confirm_btn.click()
            self.mwt()
        except TimeoutException:
            raise ErrorMsg("오류 팝업 확인 버튼을 찾을 수 없음")
        return popup_msg



    # ---------------------------
    # 법원 및 사건 선택
    # ---------------------------
    def select_court_event(self, court: str, event: str) -> None:
        """
        법원 및 사건번호 선택
        event: '2024가소619839' 형태
        """
        match = re.match(r"(\d{4})([가-힣]+)(\d+)", event)
        if not match:
            raise ValueError(f"잘못된 사건번호 형식: {event}")
        year, sign, sn = match.groups()

        # 법원 선택
        Select(self.driver.find_element(By.ID, "mf_pfwork_sbx_cortList")).select_by_visible_text(court)
        self.swt()

        # 사건 연도, 구분, 번호 입력
        Select(self.driver.find_element(By.ID, "mf_pfwork_sbx_csYear")).select_by_visible_text(year)

        event_type_elem = self.wait.until(
            EC.element_to_be_clickable((By.ID, "mf_pfwork_acp_csDvs_input"))
        )
        event_type_elem.clear()
        event_type_elem.send_keys(sign)
        self.swt()

        event_sn_elem = self.wait.until(
            EC.element_to_be_clickable((By.ID, "mf_pfwork_ibx_csNo"))
        )
        event_sn_elem.clear()
        event_sn_elem.send_keys(sn)
        self.swt()