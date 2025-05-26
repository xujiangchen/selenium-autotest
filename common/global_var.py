import time

from selenium.webdriver.remote.webdriver import WebDriver


class GlobalVar:
    driver = None
    driver_map = {}

    @classmethod
    def get_driver(cls) -> "WebDriver":
        if cls.driver is None:
            raise ValueError("没有发现可用的driver，请先调用set_driver的方法")
        return cls.driver

    @classmethod
    def set_driver(cls, driver: WebDriver) -> None:
        if cls.get_driver_map("base") is None:
            cls.set_driver_map("base", driver)
        cls.driver = driver

    @classmethod
    def set_driver_map(cls, driver_role, driver):
        cls.driver_map[driver_role] = driver

    @classmethod
    def get_driver_map(cls, driver_role):
        return cls.driver_map[driver_role]

    @classmethod
    def switch_driver(cls, driver_role):
        if cls.driver_map.get(driver_role, None) is not None:
            cls.driver.minimize_window()
            cls.driver = cls.driver_map.get(driver_role, None)
            time.sleep(1)
            cls.driver.maximize_window()

    @classmethod
    def cleanup_driver(cls):
        for key, value in cls.driver_map.items():
            try:
                value.quit()
            except Exception as e:
                print(f"退出驱动失败:{key},{e}")
            cls.driver_map = {}
            cls.driver = None
