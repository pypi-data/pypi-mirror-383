import os
# from ysnetconf.tests.sel_base_class import Driver
# from django.contrib.auth.models import User
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from yangsuite.paths import set_base_path
import unittest


dir = os.path.dirname(os.path.abspath(__file__))
sc_path = os.path.join(dir, 'screenshots')


class TestNetconfAutomation(StaticLiveServerTestCase, unittest.TestCase):
    testdir = os.path.join(os.path.dirname(__file__), 'data')
    loggedInUser = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wdriver = webdriver
        # cls.driver = Driver(sc_path)
        # cls.driver.initialize_webdriver('firefox')
        # User.objects.create_superuser('test', 'admin@localhost',
        #                               'selenium-test@123')
        set_base_path(cls.testdir)
        # cls.driver.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        # cls.driver.driver.quit()
        super().tearDownClass()

    @unittest.skip('Selenium tests cannot find Firefox binary.')
    def test_login_page(self):
        try:
            self.username = 'test'
            self.password = 'selenium-test@123'
            self.email = 'admin@localhost'
            self.driver.driver.get('%s%s' % (self.live_server_url,
                                   '/accounts/login/'))
            self.driver.sendkeys("//input[@id='id_username']", self.username)
            self.driver.sendkeys("//input[@id='id_password']", self.password)
            self.driver.click_on("//input[@class='btn btn-primary']",
                                 'clicking on submit password')
            self.driver.wait_for_element("//a[@class='avatar']", 'Login')
            loggedInUser = self.driver.by_locator("//a[@class='avatar']")

            if loggedInUser:
                self.assertEquals(loggedInUser.text,
                                  self.username,
                                  "Login Failed"
                                  )
                print("Login Sucessfull")
                self.driver.loggedInUser = loggedInUser.text
                self.driver.driver.get('%s%s' % (self.live_server_url,
                                                 '/netconf/getyang/'))
                self.driver.click_on("//*[contains(@id, 'ytool-yangset')]",
                                     'clicking on dropdown yangset')
                self.driver.click_on("//*[contains(@id, 'ytool-yangset')]"
                                     "//child::option[2]",
                                     'selecting yangset')
                self.driver.click_on("//*[contains(@id, "
                                     "'ytool_models_chosen')]",
                                     'clicking on dropdown to choose module')
                self.driver.click_on("//*[contains(@id, "
                                     "'ytool_models_chosen')]"
                                     "//child::li[normalize-space(text())="
                                     "'openconfig-network-instance']",
                                     'selecting openconfig-network-instance ')
                self.driver.click_on("//input[@id='ys-load-modules']",
                                     'clicking on submit')
                self.driver.click_on("//select[@id='ys-devices-replay']"
                                     "//child::option"
                                     "[@value='new-device-csr']",
                                     'clicking on Devices')
                self.driver.click_on("//li[@id=1]"
                                     "//child::i[@class="
                                     "'jstree-icon jstree-ocl'"
                                     "and @role='presentation']",
                                     'expanding the tree')
                # self.driver.click_on("//div[@data-jstreegrid = '150']",
                #                      'Enable leafref "name"')
                # self.driver.click_on("//input[@type='text'"
                #                      "and @nodeid='150']",
                #                      'expanding the tree')
                # self.driver.sendkeys("//input[@nodeid=150]", 'Name')
                # self.driver.click_on("//*[contains(@id,151)]"
                #                      "//child::i[contains(@class,"
                #                      "'jstree-icon jstree-ocl')]",
                #                      'expanding the Config')
                # self.driver.click_on("//div[@data-jstreegrid = '152']",
                #                      'Enable leaf "name"')
                # self.driver.click_on("//input[@type='text' "
                #                      "and @nodeid='152']",
                #                      'clicking leaf "name ')
                # self.driver.sendkeys("//input[@nodeid=152]", 'Name')
                # self.driver.click_on("//div[@data-jstreegrid = '154']",
                #                      'Click on enabled')
                # self.driver.click_on("//*[contains(@nodeid,'154')]"
                #                      "//child::option[1]",
                #                      'Select value in enabled')
                # self.driver.click_on("//*[contains(@id,"
                #                      "'ys-open-device-window')]"
                #                      "//child::option[1]",
                #                      'Open in new window')
                # self.driver.click_on("//*[contains(@id,'ys-proto-op')]"
                #                      "//child::option[2]",
                #                      'Select Edit-op')
                # self.driver.click_on("//*[contains(@id, '_grid_150_col2')]",
                #                      'Enable OP')
                # self.driver.click_on("//*[contains(@id, '_grid_150_col2')]"
                #                      "//select[@nodeid = '150']"
                #                      "//child::option[1]",
                #                      'Select merge')
                # self.driver.click_on("//*[contains(@id,'ys-build-rpc-btn')]",
                #                      'clicking on build rpc')
                # self.driver.click_on("//*[contains(@id,'ys-run-rpcs-btn')]",
                #                      'clicking on run rpc')
                # self.driver.driver.implicitly_wait(20)
                # # Get Parent window handle
                # handles = self.driver.driver.window_handles
                # self.driver.driver.switch_to.window(handles[0])
                # self.driver.driver.implicitly_wait(20)
                # self.driver.click_on("//*[contains(@id,'ys-clear-rpcs-btn')]",
                #                      'clicking on clear')
            else:
                print("Login Failure")
                raise Exception('Error')
        except Exception as e:
            raise Exception("Error on Selenium Test." + str(e))
