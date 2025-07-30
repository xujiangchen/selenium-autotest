import os

import pytest

from common.driver_config import DriverConfig
from common.global_var import GlobalVar

# 所有case运行前获取驱动的前置方法
@pytest.fixture(scope="class", autouse=True)
def driver():
    debugger = False  # 调试模式，用于接管cmd启动的浏览器，方便调试
    browser_type = os.environ['TEST_BROWSER']  # 获取浏览器类型
    global get_driver  # 设置全局变量
    get_driver = DriverConfig().init_driver(browser_type, debugger)  # 初始化驱动
    GlobalVar.set_driver(get_driver)  # 将驱动放入 GlobalVar 中
    yield get_driver
    GlobalVar.cleanup_driver()  # case 全部运行完成后，将所有的驱动都销毁
