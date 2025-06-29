import json
import os.path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chromium.options import ChromiumOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from utils.file_utils import get_current_project_path
from utils.log_manager import LogManager

logger = LogManager()


class DriverConfig:

    @staticmethod
    def default_chrome_options(options: ChromiumOptions = None, debugger=False):
        if debugger:
            # debugger模式，接管浏览器，方便调试Test case
            options.debugger_address = "127.0.0.1:9222"
        else:
            download_dir = os.path.join(get_current_project_path(), "download")  # 设置浏览器下载文件路径
            prefs = {
                'profile.default_content_settings.popups': 0,  # 禁止所有弹窗显示（0表示阻止）
                'profile.default_content_setting_values.notifications': 2,  # 禁用浏览器通知（2表示阻止）
                'download.default_directory': download_dir,  # 设置默认下载目录路径
                'safebrowsing.enabled': True,  # 启用谷歌安全浏览保护功能
                'download.prompt_for_download': False,  # 下载时不显示确认弹窗
                'profile.default_content_setting_values.automatic_downloads': 1  # 允许自动下载（1表示允许）
            }
            options.add_argument('--safebrowsing-disable-download-protectio‌​n')  # 禁用下载文件的类型安全检测
            options.add_argument('--test-type')  # 标记为测试模式，规避部分浏览器限制
            options.add_argument('--start-maximized')  # 启动时最大化窗口
            options.add_argument('no-default-browser-check')  # 跳过默认浏览器检查
            options.add_argument('disable-popup-blocking​')  # 完全禁用弹窗拦截功能
            options.add_argument('--lang=en_US')  # 设置浏览器语言为美式英语
            options.add_argument('--ignore-certificate-errors')  # 跳过SSL/TLS证书验证环节
            options.add_experimental_option('prefs', prefs)
        return options

    def chrome_driver_config(self, debugger=None):
        options = webdriver.ChromeOptions()
        driver_json_path = os.path.join(get_current_project_path(), 'selenium', 'chromedriver', '.wdm', 'drivers.json')
        try:
            with open(driver_json_path, encoding='uft-8') as a:
                result = json.load(a)
                for key in result.keys():
                    if 'win32_chromedriver' in key:
                        chrom_driver = result[key].get('binary_path')
                        service = ChromeService(chrom_driver)
                        driver = webdriver.Chrome(service=service, options=self.default_chrome_options(options, debugger))
        except Exception as e:
            # 如果本地驱动查找或启动失败，则自动下载符合版本的驱动
            logger.error(f"本地驱动启动浏览器失败 {e}")
            service = ChromeService(self.safe_chromedriver_install())
            driver = webdriver.Chrome(service=service, options=self.default_chrome_options(options, debugger))
        driver.delete_all_cookies()
        driver.maximize_window()
        return driver

    @staticmethod
    def safe_chromedriver_install():
        # 修复 webdriver-manager 4.x bug
        chrome_driver_path = os.path.join(get_current_project_path(), 'selenium', 'chromedriver')
        path = ChromeDriverManager(cache_manager=DriverCacheManager(chrome_driver_path, 30)).install()
        correct_exe_path = os.path.join(os.path.dirname(path), "chromedriver.exe")

        modified = False
        driver_json_path = os.path.join(get_current_project_path(), 'selenium', 'chromedriver', '.wdm', 'drivers.json')
        if os.path.exists(driver_json_path):
            with open(driver_json_path, encoding='uft-8') as f:
                drivers_data = json.load(f)
            for key, value in drivers_data:
                bin_path = value.get("binary_path", '')
                if bin_path.endswith("THIRD_PARTY_NOTICES.chromedriver"):
                    drivers_data[key]["binary_path"] = correct_exe_path
                    modified = True
        if modified:
            with open(driver_json_path, 'w', encoding="utf-8 ") as f:
                json.dump(drivers_data, f, indent=4)
        return correct_exe_path
