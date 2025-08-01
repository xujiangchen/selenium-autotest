import os

import allure
import pytest

from common.driver_config import DriverConfig
from common.global_var import GlobalVar
from utils.common_utils import get_host_ip_address
from utils.log_manager import LogManager
from utils.screen_recording import ScreenRecording
from utils.time_utils import get_utc_date_str, TimeFormat

logger = LogManager()

# 获取当前项目所在根目录并创建一个 testData的文件夹用于存储录屏信息
server_local_path = os.path.splitdrive(os.getcwd())[0] + "\\testData"


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


# 这个是执行每个case 的时候进行录屏，
@pytest.fixture(autouse=True)
def capture_case_recording(request):
    """
    如果想要使用这个前置条件
        - case 必须在windows 商执行，并且屏幕不能锁屏
    完成后，会在allure报告中生成一个url，如果想点击查看就要打开windows测试机的 FTP 功能，不然就只能登录测试机器上看
    """
    test_name = request.node.name
    screen_record = None
    try:
        video_name = f"{test_name}_{get_utc_date_str(TimeFormat.YYYYMMDD_HHMMSS.value)}.mp4"
        save_path = os.path.join(server_local_path, 'screen_record')
        screen_record = ScreenRecording(video_name=video_name, save_path=save_path)
        screen_record.start()
    except Exception as e:
        logger.info(f"start recording failed: {str(e)}")
        screen_record = None

    yield

    if screen_record:
        try:
            screen_record.stop()
            http_path = f"https://{get_host_ip_address()}{screen_record.file_name.replace(server_local_path, "")}".replace("\\", '/')
            allure.attach(name="Case Recording", body=http_path, attachment_type=allure.attachment_type.URI_LIST)
        except Exception as e:
            logger.info(f"stop recording failed: {str(e)}")
