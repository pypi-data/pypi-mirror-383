import logging
import traceback
import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import platform as py_platform
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("This is an info message")
testdir = os.path.dirname(os.path.abspath(__file__))
sc_path = os.path.join(testdir, 'screenshots')
fixtures_dir = os.path.join(testdir, 'fixtures')


def platform():
    """Returns the platform

    :returns: Either one of OSX, WIN, LINUX
    """
    platform_str = py_platform.platform().lower()
    if "mac" in platform_str or "darwin" in platform_str:
        return "OSX"
    elif "windows" in platform_str or "win32" in platform_str:
        return "WIN"
    else:
        return "LINUX"


class Driver(object):

    screenshot_path = None

    def __init__(self, screenshot_path):
        self.screenshot_path = screenshot_path
        self.logger = logger
        self.driver = webdriver
        self.platform = platform()
        if self.platform == 'OSX':
            self.gecko_dir = os.path.join(
                fixtures_dir, 'firefox-mac', 'geckodriver'
            )
        elif self.platform == 'LINUX':
            self.gecko_dir = os.path.join(
                fixtures_dir, 'firefox-linux', 'geckodriver'
            )
        self.loggedInUser = None

    def initialize_webdriver(self, browser_type="chrome"):
        options = Options()
        options.headless = True

        if self.platform == "WIN" and browser_type == 'ie':
            self.driver = webdriver.Ie()
        elif browser_type == 'firefox':
            binary = FirefoxBinary('/auto/ddmi/firefox/firefox/firefox-bin')
            self.driver = webdriver.Firefox(
                options=options,
                executable_path=self.gecko_dir,
                firefox_binary=binary
            )
        elif browser_type == 'chrome':
            chrome_options = Options()
            chrome_options.add_argument("window-size=1024,768")

            if platform() == "WIN":
                os.system("taskkill /f /im chromedriver.exe")
                chromedriver_path = self.driver_path

            else:
                chromedriver_path = self.driver_path

            self.driver = webdriver.Chrome(chromedriver_path,
                                           chrome_options=chrome_options)
            self.driver.implicitly_wait(5)
            self.driver.maximize_window()
        else:
            raise Exception('unknown webdriver type')
        return self.driver

    def wait_some_time(self, time_val=5):
        self.driver.implicitly_wait(time_val)

    def navigate_to_url(self, url):
        try:
            self.driver.get(url)
        except Exception as e:
            logger.error("url", e)

            print(e)

    def close_browser(self):
        try:
            self.driver.close()
        except Exception as e:

            logger.error('browser not close', e)

    def by_locator(self, loc):
        try:
            if loc.startswith('name='):
                loc = loc.replace('name=', '')
                return self.driver.find_element_by_name(loc)
            if loc.startswith('P='):
                loc = loc.replace('P=', '')
                return self.driver.find_element_by_partial_link_text(loc)
            if loc.startswith('class='):
                loc = loc.replace('class=', '')
                return self.driver.find_element_by_class_name(loc)
            if loc.startswith('id='):
                loc = loc.replace('id=', '')
                return self.driver.find_element_by_id(loc)
            elif loc.startswith('//'):
                return self.driver.find_element_by_xpath(loc)
        except Exception:
            pass

    def sendkeys(self, locator, text):
        try:
            self.wait_for_element(locator, text)
            self.by_locator(locator).clear()
            self.by_locator(locator).send_keys(text)
            logger.info(f"Entered: {text}")
        except Exception as e:

            logger.error(f'unable to enter {text,e}')
            print(e)

    def wait_for_element(self, loc, text):
        try:

            wait = WebDriverWait(self.driver, 90)
            wait.until(EC.visibility_of_element_located((By.XPATH, loc)))
        except Exception as e:
            logger.error('element not found: %s exception %s' % (text, e))
            print(e)

    def click_on(self, locator, text):
        try:
            self.wait_for_element(locator, text)
            time.sleep(5)
            self.by_locator(locator).click()
            logger.info(f"Clicked on the: {text}")
        except Exception as e:
            logger.error('====failed==== unable to click %s' % text,
                         traceback.format_exc(e))
            print(e)
