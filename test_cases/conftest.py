import pytest

from common.driver_config import DriverConfig
from common.global_var import GlobalVar


# 所有case运行前，获取驱动，在case运行完成后销毁所有驱动
@pytest.fixture(scope="class", autouse=True)
def driver():
    debugger = False  # 调试模式，用于接管cmd启动的浏览器，方便调试
    global get_driver
    get_driver = DriverConfig().chrome_driver_config(debugger)
    GlobalVar.set_driver(get_driver)
    yield get_driver
    GlobalVar.cleanup_driver()
