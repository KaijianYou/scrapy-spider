import os
import time
import pickle
from typing import Dict

from scrapy_spider.settings import BASE_DIR, ZHIHU_IMAGE_DIR
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from pymouse import PyMouse

from utils.zheye import zheye
from utils.tool import save_img_from_base64_text
from utils.yundama_request import YDMRequest


def create_chrome_browser(automatic=True):
    if automatic:
        return webdriver.Chrome()
    else:
        chrome_options = Options()
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
        return webdriver.Chrome(chrome_options=chrome_options)


def login_lagou(browser):
    """利用 Selenium 模拟登录拉勾"""
    account_input = browser.find_element_by_css_selector('.form_body .input_white[type="text"]')
    password_input = browser.find_element_by_css_selector('.form_body input[type="password"]')
    submit_button = browser.find_element_by_css_selector('div[data-view="passwordLogin"] input.btn_lg')

    account_input.send_keys(os.environ['LAGOU_ACCOUNT'])
    time.sleep(2)
    password_input.send_keys(os.environ['LAGOU_PASSWORD'])
    time.sleep(2)
    submit_button.click()


def get_lagou_cookie() -> Dict[str, str]:
    """获取拉勾网登录后的 Cookie"""
    cookie_path = os.path.join(BASE_DIR, 'lagou.cookie')
    # TODO: Cookie 失效的情况
    if os.path.isfile(cookie_path):
        with open(cookie_path, 'rb') as f:
            cookies = pickle.load(f)
    else:
        browser = create_chrome_browser()
        try:
            browser.maximize_window()
        except Exception:
            pass

        browser.get('https://passport.lagou.com/login/login.html')
        login_lagou(browser)
        time.sleep(10)  # 等待可能登录成功后的页面加载

        cookies = browser.get_cookies()
        browser.quit()
        with open(cookie_path, 'wb') as f:
            pickle.dump(cookies, f)

    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie['name']] = cookie['value']

    return cookie_dict


def login_zhihu(browser):
    """利用 Selenium 模拟登录知乎"""
    account_input = browser.find_element_by_css_selector('.SignFlow-accountInput input[name="username"]')
    password_input = browser.find_element_by_css_selector('.SignFlow-password input[name="password"]')
    submit_button = browser.find_element_by_css_selector('button.SignFlow-submitButton')

    account_input.send_keys(Keys.COMMAND + 'a')
    account_input.send_keys(os.environ['ZHIHU_ACCOUNT'])
    # 先提交错误密码，使验证码出现
    account_input.send_keys(Keys.COMMAND + 'a')
    password_input.send_keys(os.environ['ZHIHU_WRONG_PASSWORD'])
    submit_button.click()

    time.sleep(2)

    account_input.send_keys(Keys.COMMAND + 'a')
    password_input.send_keys(os.environ['ZHIHU_CORRECT_PASSWORD'])
    submit_button.click()


def get_zhihu_cookie() -> Dict[str, str]:
    """获取知乎登录后的 Cookie
    知乎可以检测到 Selenium
    1. 手动启动 Chrome（通过命令：chrome.exe --remote-debugging-port=9222 --user-data-dir=remote-profile）
    2. 确保上一步成功后再执行此函数
    """
    cookie_path = os.path.join(BASE_DIR, 'zhihu.cookie')
    # TODO: Cookie 失效的情况
    if os.path.isfile(cookie_path):
        with open(cookie_path, 'rb') as f:
            cookies = pickle.load(f)
    else:
        browser = create_chrome_browser(automatic=False)
        try:
            browser.maximize_window()
        except Exception:
            pass

        m = PyMouse()

        browser.get('https://www.zhihu.com/signin')
        login_zhihu(browser)
        time.sleep(10)  # 等待可能登录成功后的页面加载

        browser_nav_panel_height = browser.execute_script('return window.outerHeight - window.innerHeight;')

        while True:
            # 判断页面上是否能找到用户头像的元素，如果能，则说明登录成功；反之，则登录失败
            try:
                browser.find_element_by_css_selector('img.AppHeader-profileAvatar')
            except Exception:
                pass
            else:
                break

            # 登录失败，可能弹出验证码
            # 验证码有英文验证码和中文验证码两种，需要两种都判断一下
            try:
                english_captcha = browser.find_element_by_css_selector('img.Captcha-englishImg')
            except Exception:
                pass
            else:
                captcha_src = english_captcha.get_attribute('src')
                captcha_file_path = os.path.join(ZHIHU_IMAGE_DIR, 'captcha_en.jpeg')
                save_img_from_base64_text(captcha_src, captcha_file_path)
                # 不停尝试打码，直到返回的结果非空
                while True:
                    code = YDMRequest.decode(captcha_file_path, 5000)
                    if code:
                        break
                captcha_input = browser.find_element_by_css_selector('div.SignFlow-captchaContainer input[name="captcha"]')
                captcha_input.send_keys(code)

            try:
                chinese_captcha = browser.find_element_by_css_selector('img.Captcha-chineseImg')
            except Exception:
                pass
            else:
                captcha_src = chinese_captcha.get_attribute('src')
                captcha_file_path = os.path.join(ZHIHU_IMAGE_DIR, 'captcha_cn.jpeg')
                save_img_from_base64_text(captcha_src, captcha_file_path)
                captcha_location = chinese_captcha.location
                left = captcha_location['x']
                top = captcha_location['y']
                # 浏览器导航栏的宽度
                captcha_hint_height = 0
                try:
                    captcha_hint_element = browser.find_element_by_css_selector('div.Captcha-chinese div.Captcha-info')
                except Exception:
                    pass
                else:
                    captcha_hint_height = float(captcha_hint_element.getAttribute("naturalHeight"))
                print(captcha_hint_height)

                z = zheye()
                positions = z.Recognize(captcha_file_path)
                for position in positions:
                    m.move(left+position[1]/2, top+browser_nav_panel_height+position[0]/2+captcha_hint_height)
                    m.click(left+position[1]/2, top+browser_nav_panel_height+position[0]/2+captcha_hint_height)

            login_zhihu(browser)
            time.sleep(8)  # 等待可能登录成功后的页面加载

        time.sleep(15)

        browser.get('https://www.zhihu.com/')
        cookies = browser.get_cookies()

        browser.quit()
        with open(cookie_path, 'wb') as f:
            pickle.dump(cookies, f)

    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie['name']] = cookie['value']

    return cookie_dict
