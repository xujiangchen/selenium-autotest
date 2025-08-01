import json
import os.path
import subprocess
import winreg
import zipfile

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chromium.options import ChromiumOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from selenium.webdriver.edge.options import Options as EdgeOption
from selenium.webdriver.edge.service import Service as EdgeService

from utils.file_utils import get_current_project_path
from utils.log_manager import LogManager

logger = LogManager()

edge_driver_path = os.path.join(get_current_project_path(), 'selenium', 'edgedriver')


class DriverConfig:

    def init_driver(self, browser_type="Chrome", debugger=None):
        driver = None
        if browser_type.lower() == "chrome":
            driver = self.init_chrome_driver(debugger)
        elif browser_type.lower() == "firefox":
            # TODO
            pass
        elif browser_type.lower() == "edge":
            driver = self.init_edge_driver(debugger)
        return driver

    # =================================================== Chrome 浏览器 =================================================================
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

    def init_chrome_driver(self, debugger=None):
        options = webdriver.ChromeOptions()
        try:
            driver_json_path = os.path.join(get_current_project_path(), 'selenium', 'chromedriver', '.wdm', 'drivers.json')
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

    # =================================================== Edge 浏览器 =================================================================
    @staticmethod
    def default_edge_options(edge_options: EdgeOption = None, debugger=False):
        if debugger:
            # debugger模式，接管浏览器，方便调试Test case
            edge_options.debugger_address = "127.0.0.1:9222"
        else:
            edge_options.add_argument('start-maximized')
            edge_options.add_argument('disable-infobars')
            edge_options.add_argument('--disable-extensions')
            download_dir = os.path.join(get_current_project_path(), "download")
            prefs = {
                'profile.default_content_settings.popups': 0,  # 阻止弹窗（0=阻止，1=允许）
                'profile.default_content_setting_values.notifications': 2,  # 禁用通知（2=阻止，1=允许）
                'download.default_directory': download_dir,  # 默认下载路径（需替换为实际路径）
                'download.prompt_for_download': False,  # 禁止下载确认弹窗
                'download.directory_upgrade': True,  # 允许覆盖旧版下载目录设置
                'profile.default_content_setting_values.automatic_downloads': 1,  # 允许自动下载（1=允许，2=阻止）
                'safebrowsing.enabled': True,  # 启用安全浏览（Edge 可能忽略此选项，因默认开启）
                'edge.preferences.enhanced': True,  # 启用 Edge 增强功能（如智能拦截）
                'browser.enable_automatic_resizing': False,  # 禁用窗口自动调整
            }
        return edge_options

    @staticmethod
    def get_edge_version():
        try:
            reg_path = r"Software\Microsoft\Edge\BLBeacon"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                version, _ = winreg.QueryValueEx(key, "version")
                return version
        except Exception as e:
            raise AssertionError(f"Get Edge version failed!")

    def download_edge_driver(self, save_dir):
        version = self.get_edge_version()
        major_version = version.split(".")[0]

        if self.get_driver_version(os.path.join(save_dir, "msedgedriver.exe")).split(".")[0] == major_version:
            return
        downlaod_url = f"https://msedgedriver.microsoft.com/{version}/edgedriver_win64.zip"
        zip_path = os.path.join(save_dir, "edgedriver.zip")

        with requests.get(downlaod_url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(save_dir)
        os.remove(zip_path)
        for root, dirs, files in os.walk(save_dir):
            for file in files:
                if file.lower() == "msedgedriver.exe":
                    driver_path = os.path.join(root, file)
                    logger.info(f"Edge driver:{driver_path}")
        raise AssertionError("not find msedgedriver.exe")

    @staticmethod
    def get_driver_version(driver_path):
        if not os.path.exists(driver_path):
            return "---"
        try:
            result = subprocess.run(
                [driver_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                result = result.stdout.strip()
                r = result.split("WebDriver")[1].split(".")[0].split()
                return r
            else:
                raise RuntimeError()
        except Exception as e:
            raise RuntimeError(f"Can not get driver version: {e}")

    def init_edge_driver(self, debugger=False):
        try:
            self.download_edge_driver(edge_driver_path)
            options = EdgeOption()
            service = EdgeService(os.path.join(edge_driver_path, "msedgedriver.exe"))
            default_driver = webdriver.Edge(options=self.default_edge_options(options, debugger), service=service)
            return default_driver
        except Exception as e:
            logger.error("Get edge driver failed!")
            return None
