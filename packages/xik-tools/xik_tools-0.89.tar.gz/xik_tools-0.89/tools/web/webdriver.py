from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os 
import logging
from .installer import Installer

class WebDriver:
    def __init__(self, headless=False):
        self.SELENIUM_URL = os.getenv('SELENIUM_URL')
        self.headless= headless
        self.driver = None
        if self.SELENIUM_URL is not None: logging.info("Using remote WebDriver.")
        self._init_chrome()

    def _init_chrome(self):
        logging.debug("Initializing Chrome WebDriver.")
        self.chrome_options = Options()
        self.chrome_options.add_argument(
            "--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'"
        )  

        if self.headless:
            self.chrome_options.add_argument('--headless=new')  # 헤드리스 모드로 실행
        self.chrome_options.add_argument('--no-sandbox')  # 사용자 네임스페이스 옵션 없이 실행
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument("--window-size=1920,1080")

        if self.SELENIUM_URL is None:
            logging.debug("Installing Chrome and ChromeDriver.")
            webdriver_path = Installer.install_chrome_and_driver()
            self.webdriver_path = webdriver_path.get('driver_path')
            self.browser_path = webdriver_path.get('chrome_path')
            logging.debug(f"ChromeDriver path: {self.webdriver_path}")
            logging.debug(f"Chrome browser path: {self.browser_path}")
        logging.debug("Chrome WebDriver initialized successfully.")
        return None
    
    def get_chrome(self):
        if self.SELENIUM_URL is None:
            self.chrome_options.binary_location = str(self.browser_path)
            service = Service(executable_path=str(self.webdriver_path))  
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        else:
            self.driver = webdriver.Remote(
                command_executor=self.SELENIUM_URL,
                options=self.chrome_options
                )
        return self.driver
    
    def move_element_to_center(self, element):
        """ 주어진 웹 요소를 뷰포트의 중앙으로 이동시킵니다. """
        logging.debug("Moving element to center.")
        driver = self.driver
        ActionChains(driver).move_to_element(element).perform()

        # 뷰포트 크기 얻기
        viewport_width = driver.execute_script("return window.innerWidth;")
        viewport_height = driver.execute_script("return window.innerHeight;")

        # 객체의 위치 얻기
        object_x = element.location['x']
        object_y = element.location['y']
        object_width = element.size['width']
        object_height = element.size['height']

        # 화면 중앙으로 이동
        target_x = object_x + object_width / 2 - viewport_width / 2
        target_y = object_y + object_height / 2 - viewport_height / 2
        driver.execute_script(f"window.scrollTo({target_x}, {target_y});")
        logging.debug(f"Element moved to center at ({target_x}, {target_y}).")
        return None

    def getDistanceScrollToBtm(self):
        """ 스크롤을 페이지 아래로 내립니다. """
        logging.debug("Scrolling to the bottom of the page.")
        driver = self.driver
        driver.find_element_by_tag_name('body').send_keys(Keys.END)
        time.sleep(1)  # 스크롤이 내려가는 동안 대기

        # 스크롤이 이동한 거리 계산
        scrollDistance = driver.execute_script("return window.pageYOffset;")
        logging.debug(f"Scrolled distance: {scrollDistance} pixels.")

        # Home 키를 눌러 시작 위치로 복귀
        driver.find_element_by_tag_name('body').send_keys(Keys.HOME)
        time.sleep(1)  # 스크롤이 위로 올라가는 동안 대기
        return scrollDistance

    def get_scroll_distance_total(self):
        def get_scroll_distance(driver):
            driver = driver
            # 현재 페이지의 스크롤 위치를 가져옵니다.
            current_scroll_position = driver.execute_script("return window.scrollY || window.pageYOffset")
            logging.debug(f"Current scroll position: {current_scroll_position} pixels.")
            
            # 스크롤 이벤트를 발생시킵니다.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            
            # 새로운 스크롤 위치를 가져옵니다.
            new_scroll_position = driver.execute_script("return window.pageYOffset")
            # 페이지 이동 거리를 계산합니다.
            scroll_distance = new_scroll_position - current_scroll_position
            logging.debug(f"Scrolled distance: {scroll_distance} pixels.")
            return scroll_distance
        
        
        """ 페이지 스크롤의 총 거리를 계산합니다. """
        logging.debug("Calculating total scroll distance.")
        total_scroll_distance = 0
        prev_scroll_distance = -1
        
        while True:
            scroll_distance = get_scroll_distance(self.driver)
            total_scroll_distance += scroll_distance
            if scroll_distance == 0 or scroll_distance == prev_scroll_distance:
                break
            prev_scroll_distance = scroll_distance
        
        # 초기 위치로 복귀하기 위해 페이지 맨 위로 스크롤합니다.
        self.driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)
        logging.debug(f"Total scroll distance: {total_scroll_distance} pixels.")
        return total_scroll_distance
    
    
    def click_action(self, element):
        driver = self.driver
        driver.execute_script("arguments[0].click();", element)
        return None