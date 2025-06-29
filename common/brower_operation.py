import io
import os
import time

from PIL import Image
from selenium.common import TimeoutException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.global_var import GlobalVar
from utils.log_manager import LogManager

logger = LogManager()


class BrowserOperator:

    def __init__(self):
        self.driver = GlobalVar.get_driver()

    def get_page_title(self):
        return self.driver.title

    def page_forward(self):
        """
        浏览器前进
        """
        self.driver.forward()

    def page_back(self):
        """
        浏览器后退
        """
        self.driver.back()

    def page_refresh(self, wait_time: int = None):
        self.driver.refresh()
        if wait_time:
            time.sleep(wait_time)

    def get_current_url(self):
        return self.driver.current_url

    def scroll_to_top(self) -> bool:
        """滑动到浏览器顶部"""
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            return True
        except Exception as e:
            raise AssertionError(f"滑动到浏览器顶部失败！{e}")

    def scroll_to_bottom(self) -> bool:
        """滑动到浏览器底部"""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            return True
        except Exception as e:
            raise AssertionError(f"滑动到浏览器底部失败！{e}")

    def get_current_handle(self):
        """
        获取当前浏览器tab的句柄
        """
        return self.driver.current_window_handle

    def get_window_handles(self):
        """
        获得当前浏览器所有窗口句柄
        """
        return self.driver.window_handles

    def switch_to_window(self, window_handle: str = None, window_index: int = -1, window_name: str = None) -> str:
        """
        切换到指定浏览器窗口
        window_handle (str): 窗口句柄（优先级最高）
        window_index (int): 窗口索引（从0开始），-1表示最后一个窗口
        window_name (str): 窗口名称（可选，通过 driver.switch_to.window(name) 实现）
        """
        try:
            # 最推荐：直接通过句柄切换
            if window_handle:
                if window_handle not in self.driver.window_handles:
                    raise AssertionError("这个浏览器句柄不存在！")
                self.driver.switch_to.window(window_handle)
                return window_handle
            # 通过名称切换（部分浏览器可能不支持）
            if window_name:
                self.driver.switch_to.window(window_name)
                return self.get_current_handle()
            # 通过索引切换
            window_handles = self.driver.window_handles
            target_index = window_index if window_index >= 0 else len(window_handles) + window_index
            if target_index < 0 or target_index >= len(window_handles):
                raise IndexError(f"Window index {window_index} out of range")
            handle = window_handles[target_index]
            self.driver.switch_to.window(handle)
            return handle
        except Exception as e:
            raise AssertionError(f"切换浏览器窗口或标签页失败! {e}")

    # ===================================================== 常用元素操作方法 start ===============================================================================

    def element_get(self, web_element: tuple, timeout=20, must_be_visible=False):
        """
        获取元素，支持等待和可见性检查
        :param web_element: 定位元组，如 (By.ID, "element_id")
        :param timeout: 超时时间（秒）
        :param must_be_visible: 是否要求元素可见
        :return: WebElement 对象
        """
        try:
            if must_be_visible:
                # 等待元素存在且可见
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located(*web_element)
                )
            else:
                # 等待元素存在
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(*web_element)
                )
            return element
        except Exception:
            raise TimeoutException(f"元素 {web_element} 在 {timeout} 秒内未找到或不可见")

    def elements_get(self, web_element: tuple, timeout=20, must_be_visible=False):
        """
        获取多个元素，支持等待和可见性检查
        :param web_element: 定位元组，如 (By.ID, "element_id")
        :param timeout: 超时时间（秒）
        :param must_be_visible: 是否要求元素可见
        :return: 包含所有匹配元素的列表
        """
        try:
            if must_be_visible:
                # 等待元素存在且可见
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_all_elements_located(*web_element)
                )
            else:
                # 等待元素存在
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located(*web_element)
                )
            return elements
        except Exception:
            raise TimeoutException(f"元素 {web_element} 在 {timeout} 秒内未找到或不可见")

    def element_wait_for_display(self, web_element: tuple, timeout=20) -> bool:
        """
        等待元素显示
        :param web_element: 定位元组，如 (By.ID, "element_id")
        :param timeout: 超时时间（秒）
        :return: WebElement 对象
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(*web_element)
            )
            return True
        except TimeoutException:
            return False
        except Exception as e:
            logger.error(f"查找元素时发生错误: {str(e)}")
            return False

    def element_wait_for_not_display(self, web_element: tuple, timeout=20):
        """
        等待元素不再显示
        :param web_element: 定位元组，如 (By.ID, "element_id")
        :param timeout: 超时时间（秒）
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(*web_element)
            )
            return True
        except TimeoutException:
            return False
        except Exception as e:
            logger.error(f"查找元素时发生错误: {str(e)}")
            return False

    def element_click(self, web_element: tuple, timeout=20):
        """
        点击元素
        web_element: 定位元组，如 (By.ID, "element_id")
        timeout: 超时时间（秒）
        """
        timeout = int(timeout / 2)  # 缩小等待时间，分成两种方式的等待，增加正确率
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(*web_element)
            )
            element.click()
        except Exception as e:
            time.sleep(1)
            logger.error(f"点击元素时发生错误， 进行重试: {str(e)}")
            element = self.element_get(web_element=web_element, timeout=timeout)
            try:
                element.click()
            except Exception as e:
                raise AssertionError(f"点击元素时发生错误: {str(e)}")

    def element_double_click(self, web_element: tuple, timeout=20):
        element = self.element_get(web_element=web_element, timeout=timeout)
        try:
            actions = ActionChains(self.driver)
            actions.double_click(element).perform()
        except Exception as e:
            raise AssertionError(f"双击元素失败: {str(e)}")

    def element_fill_value(self, web_element: tuple, value: str = "", timeout: int = 20, clear_first: bool = True, check: bool = False):
        """
        web_element (tuple): 元素定位器，格式为 (By.<strategy>, "locator_value")
        value (str): 要填写的值
        timeout (int): 等待超时时间（秒），默认20秒
        clear_first (bool): 是否先清空输入框，默认True
        check (bool): 验证输入结果，默认False
        """
        element = self.element_get(web_element, timeout)
        try:
            if value == "":
                element.clear()
                return
            if clear_first:
                element.clear()
            element.send_keys(value)
            if check:
                actual_value = element.get_attribute("value")
                if actual_value != value:
                    raise AssertionError(f"向元素{web_element}中输入内容时失败！")
        except Exception as e:
            raise AssertionError(f"向元素{web_element}中输入内容时报错: {str(e)}")

    def element_scroll_to(self, web_element: tuple, timeout=20):
        """
        滑动到指定元素位置（元素可见时停止）
        web_element: 定位元组，如 (By.ID, "element_id")
        timeout: 超时时间（秒）
        """
        element = self.element_get(web_element, timeout)
        try:
            # 使用 JavaScript 直接滚动到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'bearest'});", element)
        except Exception as e:
            raise AssertionError(f"滑动到指定元素位置失败！{e}")

    def element_send_key(self, web_element: tuple, key, timeout: int = 20):
        """
        向元素发送单个按键或组合键（如 Keys.ENTER, Keys.TAB 等）
        web_element (tuple): 元素定位器，格式为 (By.<strategy>, "locator_value")
        key (str | Keys): 要发送的按键（可以是字符串， selenium.webdriver.common.keys.Keys，或者是组合 Keys.CONTROL + "a" ）
        timeout (int): 等待超时时间（秒），默认20秒
        """
        element = self.element_get(web_element, timeout)
        try:
            # 检查 key 类型（支持字符串或 Keys）
            if isinstance(key, str):
                key = key.upper()  # 如果是字符串，转为大写（如 "enter" -> "ENTER"）
                if hasattr(Keys, key):
                    key = getattr(Keys, key)  # 转换为 Keys 枚举（如 Keys.ENTER）
                else:
                    logger.error(f"'{key}'不是标准的按键常量，将作为字符串发送")
            element.send_keys(key)
        except Exception as e:
            raise AssertionError(f"元素{web_element}触发时报错: {str(e)}")

    def element_get_attribute(self, web_element: tuple, attribute: str, timeout: int = 5):
        """
        获取元素的属性值
        web_element (tuple): 元素定位器，格式为 (By.<strategy>, "locator_value")
        attribute (str): 要获取的属性名（如 "value", "class", "href" 等）
        timeout (int): 每次尝试查找元素的超时时间（秒），默认5秒
        """
        for _ in range(3):
            try:
                element = self.element_get(web_element, timeout)
                value = element.get_attribute(attribute)
                if value is None or value == "":
                    return None
                return value
            except Exception:
                time.sleep(0.5)
                continue
        # 部分情况下没有指定的attribute也是一种期望的结果，表明前段元素处于正确的状态
        logger.error(f"{web_element} 没有发现指定的 {attribute}")
        return None

    def element_upload(self, web_element: tuple, file_path: str, timeout: int = 20):
        """
        上传文件到指定的文件输入元素
        web_element (tuple): 元素定位器，格式为 (By.<strategy>, "locator_value")
        file_path (str): 要上传的本地文件路径
        timeout (int): 每次尝试查找元素的超时时间（秒），默认20秒
        """
        if not os.path.isfile(file_path):
            raise AssertionError("指定的文件错误或者不存在！")
        # 转换为绝对路径，避免路径问题
        absolute_path = os.path.abspath(file_path)
        # 定位元素
        element = self.element_get(web_element, timeout)
        if element.get_attribute("type") != "file":
            raise AssertionError(f"该元素不是正确的文件输入框: {web_element}")
        try:
            element.send_keys(absolute_path)
        except Exception as e:
            raise AssertionError(f"上传文件错误！{e}")

    def element_save_image(self, web_element: tuple, image_file_name, timeout: int = 20):
        """
        element (WebElement): 要截图的 Selenium WebElement 对象
        image_file_name (str): 保存的图片路径 包含文件名（支持 .png/.jpg/.jpeg）
        """
        ext = os.path.splitext(image_file_name)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg"):
            raise ValueError("图片名称必须以： .png, .jpg, or .jpeg 结尾")
        os.makedirs(os.path.dirname(image_file_name), exist_ok=True)

        element = self.element_get(web_element, timeout)
        try:
            # 获取元素截图（返回二进制数据）
            element_screenshot = element.screenshot_as_png
            if ext == ".png":
                with open(image_file_name, "wb") as f:
                    f.write(element_screenshot)
            else:
                img = Image.open(io.BytesIO(element_screenshot))
                img.save(image_file_name)
        except Exception as e:
            raise AssertionError(f"保存元素 {web_element} 失败！{e}")

    def element_move_mouse_to(self, web_element: tuple, timeout=20):
        """
        将鼠标移动到指定元素中心位置
        web_element: 定位元组，如 (By.ID, "element_id")
        timeout: 超时时间（秒）
        """
        element = self.element_get(web_element, timeout)
        try:
            ActionChains(self.driver).move_to_element(element).perform()
        except Exception as e:
            raise AssertionError(f"将鼠标移动到指定元素中心位置失败！{e}")

    # ===================================================== 常用元素操作方法 end   ===============================================================================

    def execute_javascript(self, js, *args):
        """
        执行 JavaScript 代码并返回结果
        """
        if not js or not isinstance(js, str):
            raise ValueError("JavaScript 内容错误！")
        try:
            # 执行 JavaScript 并返回结果
            result = self.driver.execute_script(js, *args)
            return result
        except Exception as e:
            raise AssertionError("执行JavaScript脚本报错！")

    def action_send_key(self, action_keys: list):
        """
        模拟键盘按键操作（支持组合键、序列输入）
        action_keys (list): 按键序列，例如：
            - 单键: ["a"], ["ENTER"]
            - 组合键: [Keys.CONTROL, "a"] (全选)
            - 序列: ["hello", Keys.TAB, "world"]
        """
        try:
            actions = ActionChains(self.driver)
            for key in action_keys:
                if not self._is_valid_key(key):
                    raise ValueError(f"无效按键: {key}.")
                if key in [Keys.CONTROL, Keys.SHIFT, Keys.ALT, Keys.COMMAND]:
                    actions.key_down(key)
                else:
                    actions.send_keys(key)
            actions.perform()
        except Exception as e:
            raise AssertionError(f"模拟键盘操作失败！{e}")

    @staticmethod
    def _is_valid_key(key) -> bool:
        """检查按键是否合法（Keys.* 或单字符字符串）"""
        if isinstance(key, str) and len(key) == 1:
            return True  # 普通字符（如 "a", "1"）
        if hasattr(Keys, key) if isinstance(key, str) else False:
            return True  # Keys 枚举（如 Keys.ENTER）
        return False
