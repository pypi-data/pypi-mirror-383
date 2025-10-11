"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: selenium.py
@Time: 2023/12/9 18:00
"""
import os
import platform
from time import sleep, time

import allure
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from SteamedBun import logger
from SteamedBun._Poium.config import BrowserObject
from SteamedBun._Poium.universal.exceptions import DriverNoneException
from SteamedBun._Poium.universal.exceptions import FindElementTypesError
from SteamedBun._Poium.universal.exceptions import FuncTimeoutException
from SteamedBun._Poium.universal.exceptions import PageElementError
from SteamedBun._Poium.universal.func_timeout import func_timeout
from SteamedBun._Poium.universal.selector import selection_checker

# Map PageElement constructor arguments to webdriver locator enums
LOCATOR_LIST = {
    # selenium
    'css': By.CSS_SELECTOR,
    'id_': By.ID,
    'name': By.NAME,
    'xpath': By.XPATH,
    'link_text': By.LINK_TEXT,
    'partial_link_text': By.PARTIAL_LINK_TEXT,
    'tag': By.TAG_NAME,
    'class_name': By.CLASS_NAME,

}

BY_LIST = [
    # selenium
    By.CSS_SELECTOR,
    By.ID,
    By.NAME,
    By.XPATH,
    By.LINK_TEXT,
    By.PARTIAL_LINK_TEXT,
    By.TAG_NAME,
    By.CLASS_NAME
]


def _auto_screenshot(elem, context, describe=""):
    from SteamedBun import processing, case_attach

    window_size = context.get_window_size()
    window_width, window_height = window_size.get("width") - 14, window_size.get("height") - 140
    _rect: dict = elem.rect
    elem_x, elem_y = _rect.get("x", 0), _rect.get("y", 0)
    _, elem_height = _rect.get("width", 0), _rect.get("height", 0) / 4
    filename = f"{describe or 'selenium'}_screenshot_{int(time() * 1000)}.png"
    filename = os.path.join(BrowserObject.selenium_screenshot_path, filename)
    context.save_screenshot(filename=filename)
    processing(
        filename=filename,
        w=elem_x / window_width,
        h=(elem_y + elem_height) / window_height
    )
    case_attach(
        body=open(file=filename, mode="rb").read(),
        name=filename,
        attachment_type=allure.attachment_type.PNG
    )


class BasePage:
    """
    Page Object pattern.
    """

    def __init__(self, driver=None, url: str = None):
        """
        :param driver: `selenium.webdriver.WebDriver` Selenium webdriver instance
        :param url: `str`
        """
        self.driver = None
        if driver is not None:
            self.driver = driver
        else:
            ...

        if self.driver is None:
            raise DriverNoneException("driver is None, Please set selenium/appium driver.")
        self.root_uri = url if url else getattr(self.driver, 'url', None)

    def get(self, uri: str) -> None:
        """
        go to uri
        :param uri: URI to GET, based off of the root_uri attribute.
        :return:
        """
        root_uri = self.root_uri or ''
        self.driver.get(root_uri + uri)
        self.driver.implicitly_wait(5)

    def open(self, uri: str) -> None:
        """
        open uri
        :param uri:  URI to GET, based off of the root_uri attribute.
        :return:
        """
        root_uri = self.root_uri or ''
        self.driver.get(root_uri + uri)
        logger.info(f'正在进入【{uri}】网站')
        self.driver.implicitly_wait(5)

    def refresh(self):
        self.driver.refresh()
        logger.info("✅ 刷新窗口")

    def maximize_window(self):
        """
        Maximizes the current window that webdriver is using
        """
        self.driver.maximize_window()
        logger.info("✅ 窗口最大化")

    def minimize_window(self):
        """
        Invokes the window manager-specific 'minimize' operation
        """
        self.driver.minimize_window()
        logger.info("✅ 窗口最小化")

    def close(self):
        """
            Closes the current window.
        """
        self.driver.close()
        logger.info("✅ 关闭当前窗口")

    def quit(self):
        """
            Quits the driver and closes every associated window.
        """
        self.driver.quit()
        logger.info("✅ 关闭浏览器")

    def fullscreen_window(self):
        """
        Invokes the window manager-specific 'full screen' operation
        """
        self.driver.fullscreen_window()
        logger.info("✅ 窗口最大化")

    def get_screenshot_as_png(self):
        """
        Gets the screenshot of the current window as a binary data.
        """
        _ = self.driver.get_screenshot_as_png()
        logger.info("✅ 截图当前窗口 以二进制的形式")
        return _

    def get_screenshot_as_base64(self):
        """
        Gets the screenshot of the current window as a base64 encoded string
           which is useful in embedded images in HTML.
        """
        _ = self.driver.get_screenshot_as_base64()
        logger.info("✅ 截图当前窗口 以base64的形式")
        return _


class Element(object):
    """
    Returns an element object
    """

    def __init__(self,
                 selector: str = None,
                 id_: str = "",
                 name: str = "",
                 css: str = "",
                 xpath: str = "",
                 class_name: str = "",
                 timeout: int = 3,
                 describe: str = "",
                 index: int = 0,
                 **kwargs):
        self.selector = selector
        self.times = timeout
        self.index = index
        self.desc = describe
        self.exist = False

        if selector is not None:
            self.k, self.v = selection_checker(selector)
        else:
            if id_:
                kwargs['id_'] = id_
            elif name:
                kwargs['name'] = name
            elif css:
                kwargs['css'] = css
            elif xpath:
                kwargs['xpath'] = xpath
            elif class_name:
                kwargs['class_name'] = class_name
            if not kwargs:
                raise ValueError(f"Please specify a locator from {LOCATOR_LIST}")
            if len(kwargs) > 1:
                raise ValueError(f"Please specify only one locator from {LOCATOR_LIST}")
            self.kwargs = kwargs
            by, self.v = next(iter(kwargs.items()))

            self.k = LOCATOR_LIST.get(by, None)
            if self.k is None:
                raise FindElementTypesError("Element positioning of type '{}' is not supported.".format(self.k))

    def __get__(self, instance, owner):
        if instance is None:
            return None

        BrowserObject.driver = instance.driver
        return self

    def __set__(self, instance, value):
        self.__get__(instance, instance.__class__)
        self.send_keys(value)

    @func_timeout(1)
    def find_elements_timeout(self, key: str, value: str):
        try:
            return BrowserObject.driver.find_elements(key, value)
        except Exception as e:
            return [] and e

    def find(self, by: str, value: str) -> list:
        """
        Find if the element exists.
        """
        for i in range(self.times):
            try:
                elems = self.find_elements_timeout(by, value)
                break
            except FuncTimeoutException:
                sleep(1)
        else:
            elems = []

        if len(elems) == 1:
            logger.info(f"🔍 Find element: {by}={value}. {self.desc}")
        elif len(elems) > 1:
            logger.info(f"❓ Find {len(elems)} elements through: {by}={value}. {self.desc}")
        else:
            logger.warning(f"❌ Find 0 elements through: {by}={value}. {self.desc}")

        return elems

    def __get_element(self, by: str, value: str):
        """
        Judge element positioning way, and returns the element.
        """

        if by in BY_LIST:
            elem = self.find(by, value)
            if len(elem) == 0:
                self.exist = False
                return None
            else:
                self.exist = True
                elem = BrowserObject.driver.find_elements(by, value)[self.index]
        else:
            raise FindElementTypesError("Please enter the correct targeting elements")

        if BrowserObject.show is True:
            try:
                style_red = 'arguments[0].style.border="2px solid #FF0000"'
                style_blue = 'arguments[0].style.border="2px solid #00FF00"'
                style_null = 'arguments[0].style.border=""'

                BrowserObject.driver.execute_script(style_red, elem)
                sleep(0.02)
                BrowserObject.driver.execute_script(style_blue, elem)
                sleep(0.02)
                BrowserObject.driver.execute_script(style_blue, elem)
                sleep(0.01)
                BrowserObject.driver.execute_script(style_null, elem)
            except WebDriverException:
                pass

        if BrowserObject.selenium_screenshot_path:
            _auto_screenshot(elem=elem, context=BrowserObject.driver, describe=self.desc)
        return elem

    def is_exist(self) -> bool:
        """element is existed """
        self.__get_element(self.k, self.v)
        return self.exist

    def clear(self) -> None:
        """Clears the text if it's a text entry element."""
        logger.info("✅ clear.")
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ clear() error because of ❌ Find 0 elements through: {self.k}={self.v}. {self.desc}")
        elem.clear()

    def send_keys(self, value, clear=False, click=False) -> None:
        """
        Simulates typing into the element.
        If clear_before is True, it will clear the content before typing.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ send_keys() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        if click is True:
            elem.click()
            sleep(0.3)
            logger.info("✅ click().")
        if clear is True:
            elem.clear()
            sleep(0.3)
            logger.info("✅ clear().")
        elem.send_keys(value)
        logger.info(f"✅ send_keys('{value}').")

    def click(self) -> None:
        """
        Clicks the element.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ click() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        elem.click()
        logger.info("✅ click().")

    def submit(self):
        """
        Submits a form.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ submit() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        elem.submit()
        logger.info("✅ submit().")

    @property
    def tag_name(self) -> str:
        """This element's ``tagName`` property."""
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ get tag_name error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        tag_name = elem.tag_name
        logger.info(f"✅ tag_name: {tag_name}.")
        return tag_name

    @property
    def text(self) -> str:
        """The text of the element."""
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ get text error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        text = elem.text
        logger.info(f"✅ text: {text}.")
        return text

    @property
    def size(self) -> dict:
        """The size of the element."""
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ get size error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        size = elem.size
        logger.info(f"✅ size: {size}.")
        return size

    def value_of_css_property(self, property_name):
        """
        The value of a CSS property
        :param property_name:
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ get css property error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        property_value = elem.value_of_css_property(property_name)
        logger.info(f"✅ value_of_css_property('{property_name}') -> {property_value}.")
        return property_value

    def get_property(self, name) -> str:
        """
        Gets the given property of the element.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ get_property('{name}') error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        value = elem.get_property(name)
        logger.info(f"✅ get_property('{name}') -> {value}.")
        return value

    def get_attribute(self, name) -> str:
        """
        Gets the given attribute or property of the element.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ get_property('{name}') error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        value = elem.get_attribute(name)
        logger.info(f"✅ get_property('{name}') -> {value}.")
        return value

    def is_displayed(self) -> bool:
        """Whether the element is visible to a user."""
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ is_displayed() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        display = elem.is_displayed()
        logger.info(f"✅ is_displayed() -> {display}.")
        return display

    def is_selected(self):
        """
        Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ is_selected() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        select = elem.is_selected()
        logger.info(f"✅ is_selected() -> {select}.")
        return select

    def is_enabled(self):
        """Returns whether the element is enabled."""
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ is_enabled() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        enable = elem.is_enabled()
        logger.info(f"✅ is_enabled() -> {enable}.")
        return enable

    def switch_to_frame(self) -> None:
        """
        selenium API
        Switches focus to the specified frame
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ switch_to_frame() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        BrowserObject.driver.switch_to.frame(elem)
        logger.info("✅ switch_to_frame().")

    def move_to_element(self) -> None:
        """
        selenium API
        Moving the mouse to the middle of an element
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ move_to_element() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        ActionChains(BrowserObject.driver).move_to_element(elem).perform()
        logger.info("✅ move_to_element().")

    def click_and_hold(self) -> None:
        """
        selenium API
        Holds down the left mouse button on an element.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ click_and_hod() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        ActionChains(BrowserObject.driver).click_and_hold(elem).perform()
        logger.info("✅ click_and_hold().")

    def double_click(self) -> None:
        """
        selenium API
        Holds down the left mouse button on an element.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ double_click() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        ActionChains(BrowserObject.driver).double_click(elem).perform()
        logger.info("✅ double_click().")

    def context_click(self) -> None:
        """
        selenium API
        Performs a context-click (right click) on an element.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(
                f"❌ context_click() error because of Find 0 elements through: {self.k}={self.v}. {self.desc}")

        ActionChains(BrowserObject.driver).context_click(elem).perform()
        logger.info("✅ context_click().")

    def drag_and_drop_by_offset(self, x: int, y: int) -> None:
        """
        selenium API
        Holds down the left mouse button on the source element,
           then moves to the target offset and releases the mouse button.
        :param x: X offset to move to.
        :param y: Y offset to move to.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ drag_and_drop_by_offset('{x}', '{y}') error because of "
                            f"Find 0 elements through: {self.k}={self.v}. {self.desc}")

        ActionChains(BrowserObject.driver).drag_and_drop_by_offset(elem, xoffset=x, yoffset=y).perform()
        logger.info(f"✅ drag_and_drop_by_offset('{x}', '{y}').")

    def refresh_element(self, timeout: int = 5) -> None:
        """
        selenium API
        Refreshes the current page, retrieve elements.
        """
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception(f"❌ refresh_element() error because of"
                            f"Find 0 elements through: {self.k}={self.v}. {self.desc}")

        for i in range(timeout):
            if elem is not None:
                try:
                    elem
                except StaleElementReferenceException:
                    BrowserObject.driver.refresh()
                else:
                    break
            else:
                sleep(1)
        else:
            raise TimeoutError("stale element reference: element is not attached to the page document.")

    def select_by_value(self, value: str) -> None:
        """
        selenium API
        Select all options that have a value matching the argument. That is, when given "foo" this
           would select an option like:

           <option value="foo">Bar</option>

           :Args:
            - value - The value to match against

           throws NoSuchElementException If there is no option with specisied value in SELECT
        """
        select_elem = self.__get_element(self.k, self.v)
        if not select_elem:
            raise Exception(f"❌ select_by_value('{value}') error because of "
                            f"Find 0 elements through: {self.k}={self.v}. {self.desc}")

        Select(select_elem).select_by_value(value)
        logger.info(f"✅ select_by_value('{value}').")

    def select_by_index(self, index: int) -> None:
        """
        selenium API
        Select the option at the given index. This is done by examing the "index" attribute of an
           element, and not merely by counting.

           :Args:
            - index - The option at this index will be selected

           throws NoSuchElementException If there is no option with specisied index in SELECT
        """
        select_elem = self.__get_element(self.k, self.v)
        if not select_elem:
            raise Exception(f"❌ select_by_index('{index}') error because of "
                            f"Find 0 elements through: {self.k}={self.v}. {self.desc}")

        Select(select_elem).select_by_index(index)
        logger.info(f"✅ select_by_index('{index}').")

    def select_by_visible_text(self, text: str) -> None:
        """
        selenium API
        Select all options that display text matching the argument. That is, when given "Bar" this
           would select an option like:

            <option value="foo">Bar</option>

           :Args:
            - text - The visible text to match against

            throws NoSuchElementException If there is no option with specisied text in SELECT
        """
        select_elem = self.__get_element(self.k, self.v)
        if not select_elem:
            raise Exception((f"❌ select_by_visible_text('{text}') error because of "
                             f"Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        Select(select_elem).select_by_visible_text(text)
        logger.info(f"✅ select_by_visible_text('{text}').")

    def input(self, text="") -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ input('{text}') error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        elem.send_keys(text)
        logger.info(f"🎹 input('{text}').")

    def enter(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ enter() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        elem.send_keys(Keys.ENTER)
        logger.info("🎹 enter.")

    def select_all(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ select_all() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        if platform.system().lower() == "darwin":
            elem.send_keys(Keys.COMMAND, "a")
        else:
            elem.send_keys(Keys.CONTROL, "a")
        logger.info("🎹 control + a.")

    def cut(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ cut() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        if platform.system().lower() == "darwin":
            elem.send_keys(Keys.COMMAND, "x")
        else:
            elem.send_keys(Keys.CONTROL, "x")
        logger.info("🎹 control + x.")

    def copy(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ copy() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        if platform.system().lower() == "darwin":
            elem.send_keys(Keys.COMMAND, "c")
        else:
            elem.send_keys(Keys.CONTROL, "c")
        logger.info("🎹 control + c.")

    def paste(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ paste() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        if platform.system().lower() == "darwin":
            elem.send_keys(Keys.COMMAND, "v")
        else:
            elem.send_keys(Keys.CONTROL, "v")
        logger.info("🎹 control + v.")

    def backspace(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ backspace() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        elem.send_keys(Keys.BACKSPACE)
        logger.info("🎹 backspace.")

    def delete(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ delete() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        elem.send_keys(Keys.DELETE)
        logger.info("🎹 delete.")

    def tab(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ tabl() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        elem.send_keys(Keys.TAB)
        logger.info("🎹 tab.")

    def space(self) -> None:
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ space() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        elem.send_keys(Keys.SPACE)
        logger.info("🎹 space.")

    def screenshots(self, filename=None):
        """
        selenium API
        Saves a screenshots of the current element to a PNG image file
        :param filename: The file name
        """

        if filename is None:
            filename = str(time()).split(".")[0] + ".png"
        elem = self.__get_element(self.k, self.v)
        if not elem:
            raise Exception((f"❌ screenshot() error because of"
                             f" Find 0 elements through: {self.k}={self.v}. {self.desc}"))

        elem.screenshot(filename)
        logger.info("✅ screenshot.")


class Elements(object):
    """
    Returns a set of element objects
    """

    def __init__(self,
                 selector: str = None,
                 id_: str = "",
                 name: str = "",
                 css: str = "",
                 xpath: str = "",
                 class_name: str = "",
                 context: bool = False,
                 describe: str = "",
                 timeout: int = 3,
                 **kwargs):
        self.desc = describe
        self.times = timeout
        if selector is not None:
            self.k, self.v = selection_checker(selector)
        else:
            if id_:
                kwargs['id_'] = id_
            elif name:
                kwargs['name'] = name
            elif css:
                kwargs['css'] = css
            elif xpath:
                kwargs['xpath'] = xpath
            elif class_name:
                kwargs['class_name'] = class_name
            if not kwargs:
                raise ValueError("Please specify a locator")
            if len(kwargs) > 1:
                raise ValueError("Please specify only one locator")
            by, self.v = next(iter(kwargs.items()))

            self.k = LOCATOR_LIST.get(by, None)
            if self.k is None:
                raise FindElementTypesError("Element positioning of type '{}' is not supported.".format(self.k))

        self.has_context = bool(context)

    def find(self, context):
        for i in range(self.times):
            elems = context.find_elements(self.k, self.v)
            if len(elems) > 0:
                break
            else:
                sleep(1)
        else:
            elems = []

        for elem in elems:
            try:
                style_red = 'arguments[0].style.border="2px solid #FF0000"'
                style_blue = 'arguments[0].style.border="2px solid #00FF00"'
                style_null = 'arguments[0].style.border=""'

                context.execute_script(style_red, elem)
                sleep(0.02)
                context.execute_script(style_blue, elem)
                sleep(0.02)
                context.execute_script(style_blue, elem)
                sleep(0.01)
                context.execute_script(style_null, elem)
            except WebDriverException:
                pass

            if BrowserObject.selenium_screenshot_path:
                _auto_screenshot(elem=elem, context=context, describe=self.desc)

        logger.info(f"✨ Find {len(elems)} elements through: {self.k}={self.v}. {self.desc}")
        return elems

    def __get__(self, instance, owner, context=None):
        if not instance:
            return None

        if not context and self.has_context:
            return lambda ctx: self.__get__(instance, owner, context=ctx)

        if not context:
            context = instance.driver

        return self.find(context)

    def __set__(self, instance, value):
        if self.has_context:
            raise PageElementError("Sorry, the set descriptor doesn't support elements with context.")
        elems = self.__get__(instance, instance.__class__)
        if not elems:
            raise PageElementError("Can't set value, no elements found")
        [elem.send_keys(value) for elem in elems]
