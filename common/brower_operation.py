import time

from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.global_var import GlobalVar


class BrowserOperator:

    def __init__(self):
        self.driver = GlobalVar.get_driver()

    def get_element(self, web_element: tuple, timeout=20, must_be_visible=False):
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

    def get_elements(self, web_element: tuple, timeout=20, must_be_visible=False):
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
            print(f"查找元素时发生错误: {str(e)}")
            return False

    def element_wait_for_not_display(self, web_element: tuple, timeout=20):
        """
        等待元素不再显示
        :param web_element: 定位元组，如 (By.ID, "element_id")
        :param timeout: 超时时间（秒）
        :raises: TimeoutException 如果超时元素仍然显示
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(*web_element)
            )
            return True
        except TimeoutException:
            return False
        except Exception as e:
            print(f"查找元素时发生错误: {str(e)}")
            return False
