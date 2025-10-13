import os.path
import pathlib
import sys
import time
from typing import Any, Dict, List, Optional, TypedDict, Union, Pattern

import allure
from playwright._impl._element_handle import ElementHandle  # noqa
from playwright._impl._helper import (  # noqa
    KeyboardModifier,
    MouseButton,
    locals_to_params,
)
from playwright._impl._js_handle import Serializable, JSHandle  # noqa

from SteamedBun import logger
from SteamedBun._Poium.config import BrowserObject

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Literal
else:  # pragma: no cover
    from typing_extensions import Literal


class FilePayload(TypedDict):
    name: str
    mimeType: str
    buffer: bytes


class FloatRect(TypedDict):
    x: float
    y: float
    width: float
    height: float


class Position(TypedDict):
    x: float
    y: float


def _auto_screenshot_with_playwright(elem, driver, describe=""):
    from SteamedBun import processing, case_attach

    _tmp_filename = f"{describe or 'playwright'}_screenshot_{int(time.time() * 1000)}.png"
    _tmp_filename = os.path.join(BrowserObject.playwright_screenshot_path, _tmp_filename)
    driver.screenshot(path=_tmp_filename)
    position_elem = elem.bounding_box()
    elem_x, elem_y = position_elem.get("x", 0), position_elem.get("y", 0)
    viewport_size = driver.viewport_size
    viewport_width, viewport_height = viewport_size.get("width", 0), viewport_size.get("height", 0)

    processing(
        filename=_tmp_filename,
        w=elem_x / viewport_width,
        h=elem_y / viewport_height
    )

    case_attach(
        body=open(file=_tmp_filename, mode="rb").read(),
        name=_tmp_filename,
        attachment_type=allure.attachment_type.PNG
    )


class Page(object):
    """
    Page Object pattern.
    """

    def __init__(self, page):
        """
        :param page: `playwright.sync_api.Page`
        Root URI to base any calls to the ``PageObject.get`` method. If not defined
        in the constructor it will try and look it from the webdriver object.
        """
        self.page = page

    @staticmethod
    def sleep(secs=1):
        logger.info(f"等待 {secs} s.")
        return time.sleep(secs)

    def screenshot(self, filename=""):
        if not filename:
            filename = f"{int(time.time())}.png"
        logger.info(f"截图: {filename}")
        return self.page.screenshot(path=filename)

    def open(self, uri):
        """
        open uri
        :param uri:  URI to GET, based off of the root_uri attribute.
        :return:
        """
        self.page.goto(uri)

    def goto(self, uri):
        """
        goto uri
        :param uri:  URI to GET, based off of the root_uri attribute.
        :return:
        """
        self.open(uri=uri)

    def get(self, uri):
        """
        get uri
        :param uri:  URI to GET, based off of the root_uri attribute.
        :return:
        """
        self.open(uri=uri)

    def close(self):
        """
        Close the current Window Page
        """
        self.page.close()


class Locator:
    """
    Returns an element object
    """

    def __init__(
            self,
            selector: str,
            describe: str = "",
            position: Position = None,
            modifiers: List[KeyboardModifier] = None,
            delay: float = None,
            timeout: float = 1.0,
            force: bool = None,
            no_wait_after: bool = None,
            trial: bool = None,
            index: int = 0):
        self.selector = selector
        self.desc = describe
        self.position = position
        self.modifiers = modifiers
        self.delay = delay
        self.timeout = timeout * 1000
        self.force = force
        self.no_wait_after = no_wait_after
        self.trial = trial
        self.index = index

    @property
    def find(self):
        self.driver.wait_for_load_state("networkidle")
        elems = []
        for _ in range(3):
            try:
                elems = self.driver.locator(self.selector).all()
                if len(elems) != 0:
                    break
            except Exception as e:
                logger.error(f"❌ {e}")
            _ = self.timeout / 1000
            time.sleep(_)
            logger.info(f"等待 {_} s.")
        if not len(elems):
            logger.error(f"❌ 未找到对应元素. {self.desc}")
        elem = elems[self.index]
        elem.evaluate('node => node.style.cssText="border:solid 2px blue"')
        time.sleep(0.02)
        elem.evaluate('node => node.style.cssText="border:solid 2px green"')
        time.sleep(0.02)
        elem.evaluate('node => node.style.cssText="border:solid 2px red"')
        time.sleep(0.01)
        elem.evaluate('node => node.style.cssText="border:solid 2px none"')

        if BrowserObject.playwright_screenshot_path:
            _auto_screenshot_with_playwright(elem=elem, driver=self.driver, describe=self.desc)

        if self.desc == "":
            logger.info(f"✨ Find element.")
        else:
            logger.info(f"✨ Find element: {self.desc}.")
        return elem

    def __get__(self, instance, owner):
        if instance is None:
            return None

        self.driver = instance.page
        return self

    def __set__(self, instance, value):
        elem = self.__get__(instance, instance.__class__)
        elem.fill(value)

    def all_inner_texts(self) -> List[str]:
        """
        Returns an array of node.innerText values for all matching nodes.
        :return:
        """
        return self.find.all_inner_texts()

    def all_text_contents(self) -> List[str]:
        """
        Returns an array of node.textContent values for all matching nodes.
        :return:
        """
        return self.find.all_text_contents()

    def bounding_box(self) -> Optional[FloatRect]:
        """
        This method returns the bounding box of the element, or null if the element is not visible.
        :return:
        """
        return self.find.bounding_box(timeout=self.timeout)

    def fill(self, value: str) -> None:
        """
        Text input
        :param value:
        :return:
        """
        return self.find.fill(
            value=value,
            timeout=self.timeout,
            no_wait_after=self.no_wait_after,
            force=self.force,
        )

    def check(self) -> None:
        """
        Check the checkbox.
        :return:
        """
        return self.find.check(
            position=self.position,
            timeout=self.timeout,
            force=self.force,
            no_wait_after=self.no_wait_after,
            trial=self.trial,
        )

    def uncheck(self) -> None:
        """
        Uncheck by input <label>
        :return:
        """
        return self.find.uncheck(
            position=self.position,
            timeout=self.timeout,
            force=self.force,
            no_wait_after=self.no_wait_after,
            trial=self.trial
        )

    def select_option(
            self,
            value: Union[str, List[str]] = None,
            index: Union[int, List[int]] = None,
            label: Union[str, List[str]] = None,
            element: Union["ElementHandle", List["ElementHandle"]] = None,
    ) -> List[str]:
        """
        Selects one or multiple options in the <select> element.
        :return:
        """
        return self.find.select_option(
            value=value,
            index=index,
            label=label,
            element=element,
            timeout=self.timeout,
            no_wait_after=self.no_wait_after,
            force=self.force
        )

    def select_text(self) -> None:
        """
        This method waits for actionability checks,
         then focuses the element and selects all its text content.
        :return:
        """
        return self.find.select_text(
            force=self.force,
            timeout=self.timeout
        )

    async def set_checked(self, checked: bool) -> None:
        """
        This method checks or unchecks an element.
        :param checked:
        :return:
        """
        return self.find.set_checked(
            checked=checked,
            position=self.position,
            timeout=self.timeout,
            force=self.force,
            no_wait_after=self.no_wait_after,
            trial=self.trial,
        )

    def click(self, click_count: int = None, button: MouseButton = None) -> None:
        """
        click
        :param click_count:
        :param button:
        :return:
        """
        return self.find.click(
            modifiers=self.modifiers,
            position=self.position,
            delay=self.delay,
            button=button,
            click_count=click_count,
            timeout=self.timeout,
            force=self.force,
            no_wait_after=self.no_wait_after,
            trial=self.trial,
        )

    def enter(self):
        """
        模拟回车操作
        """
        return self.find.press("Enter")

    def send_keywords(self, value="", enter=False, clear=False):
        """
        send keywords、input
        """
        if clear:
            self.find.fill(value="")
        self.find.fill(value=value)
        if enter:
            self.find.press("Enter")

        return None

    def send_keyboards(self, key="Enter"):
        """
        send Mouse Key Boards
        """

        return self.find.press(key=key)

    def count(self) -> int:
        """
        Returns the number of elements matching given selector.
        :return:
        """
        return self.find.count()

    def dblclick(self, button: MouseButton = None) -> None:
        """
        double click
        :param button:
        :return:
        """
        return self.find.dblclick(
            modifiers=self.modifiers,
            position=self.position,
            delay=self.delay,
            button=button,
            timeout=self.timeout,
            force=self.force,
            no_wait_after=self.no_wait_after,
            trial=self.trial,
        )

    def drag_to(
            self,
            target: "Locator",
            source_position: Position = None,
            target_position: Position = None
    ) -> None:
        """
        Locator of the element to drag to.
        param source_position:
        param target_position:
        param target:
        :return:
        """
        return self.find.drag_to(
            target=target,
            force=self.force,
            no_wait_after=self.no_wait_after,
            timeout=self.timeout,
            trial=self.trial,
            source_position=source_position,
            target_position=target_position,
        )

    def element_handle(self) -> ElementHandle:
        """
        Resolves given locator to the first matching DOM element
        :return:
        """
        return self.find.element_handle(timeit=self.timeout)

    def element_handles(self) -> List[ElementHandle]:
        """
        Resolves given locator to all matching DOM elements.
        :return:
        """
        return self.find.element_handles()

    @property
    def first(self) -> "Locator":
        """
        Returns locator to the first matching element.
        :return:
        """
        return self.find.first

    @property
    def last(self) -> "Locator":
        """
        Returns locator to the last matching element.
        :return:
        """
        return self.find.last

    def nth(self, index: int) -> "Locator":
        """
        Returns locator to the n-th matching element. It's zero based, nth(0) selects the first element.
        :param index:
        :return:
        """
        return self.find.nth(index=index)

    @property
    def page(self) -> "Page":
        """
        A page this locator belongs to.
        :return:
        """
        return self.find.page()

    def filter(
            self,
            has_text: Union[str, Pattern[str]] = None,
            has: "Locator" = None,
    ) -> "Locator":
        """
        This method narrows existing locator according to the options.
        :param has_text:
        :param has:
        :return:
        """
        return self.find.filter(has_text=has_text, has=has)

    def get_attribute(self, name: str):
        """
        Returns element attribute value.
        :param name:
        :return:
        """
        return self.find.get_attribute(name=name, timeout=self.timeout)

    def highlight(self) -> None:
        return self.find.highlight()

    def hover(self) -> None:
        """
        Hover over element
        :return:
        """
        return self.find.hover(
            modifiers=self.modifiers,
            position=self.position,
            timeout=self.timeout,
            force=self.force,
            trial=self.trial,
        )

    def dispatch_event(self, typo: str, event_init: Dict = None) -> None:
        """
        Programmatic click
        :param typo:
        :param event_init:
        :return:
        """
        return self.find.dispatch_event(
            type=typo,
            eventInit=event_init,
            timeout=self.timeout,
        )

    def evaluate(self, expression: str, arg: Serializable = None) -> Any:
        """
        This method passes this handle as the first argument to expression.
        :param expression:
        :param arg:
        :return:
        """
        return self.find.evaluate(
            expression=expression,
            arg=arg,
            timeout=self.timeout
        )

    def evaluate_all(self, expression: str, arg: Serializable = None) -> Any:
        """
        The method finds all elements matching the specified locator and
        passes an array of matched elements as a first argument to expression.
        Returns the result of expression invocation.
        :param expression:
        :param arg:
        :return:
        """
        params = locals_to_params(locals())
        return self.find.evaluate_all(
            expression=expression,
            arg=arg
        )

    def evaluate_handle(self, expression: str, arg: Serializable = None) -> "JSHandle":
        """
        This method passes this handle as the first argument to expression.
        :param expression:
        :param arg:
        :return:
        """
        return self.find.evaluate_handle(
            expression=expression,
            arg=arg,
            timeout=self.timeout
        )

    def tap(self) -> None:
        """
        This method taps the element.
        :return:
        """
        return self.find.tap(
            modifiers=self.modifiers,
            position=self.position,
            timeout=self.timeout,
            force=self.force,
            no_wait_after=self.no_wait_after,
            trial=self.trial,
        )

    def text_content(self) -> Optional[str]:
        """
        Returns the node.textContent.
        :return:
        """
        return self.find.text_content(timeout=self.timeout)

    def type(self, text: str) -> None:
        """
        Type into the field character by character, as if it was a user with a real keyboard.
        :param text:
        :return:
        """
        return self.find.type(
            text=text,
            delay=self.delay,
            timeout=self.timeout,
            no_wait_after=self.no_wait_after,
        )

    def press(self, key: str) -> None:
        """
        Keys and shortcuts
        :param key:
        :return:
        """
        return self.find.press(
            key=key,
            delay=self.delay,
            timeout=self.timeout,
            no_wait_after=self.no_wait_after,
        )

    def set_input_files(
            self,
            files: Union[
                str,
                pathlib.Path,
                FilePayload,
                List[Union[str, pathlib.Path]],
                List[FilePayload],
            ]
    ) -> None:
        """
        Upload files
        :param files:
        :return:
        """
        return self.find.set_input_files(
            files=files,
            timeout=self.timeout,
            no_wait_after=self.no_wait_after,
        )

    def focus(self) -> None:
        """
        Focus element
        :return:
        """
        return self.find.focus(timeout=self.timeout)

    def inner_html(self) -> str:
        """
        Returns the element.innerHTML.
        :return:
        """
        return self.find.inner_html(timeout=self.timeout)

    def inner_text(self) -> str:
        """
        Returns the element.innerText.
        :return:
        """
        return self.find.inner_text(timeout=self.timeout)

    async def input_value(self) -> str:
        """
        Returns input.value for the selected <input> or <textarea> or <select> element.
        :return:
        """
        return self.find.input_value(timeout=self.timeout)

    def is_checked(self) -> bool:
        """
        Returns whether the element is checked.
        Throws if the element is not a checkbox or radio input.
        :return:
        """
        return self.find.is_checked(timeout=self.timeout)

    def is_disabled(self) -> bool:
        """
        Returns whether the element is disabled, the opposite of enabled.
        :return:
        """
        return self.find.is_disabled(timeout=self.timeout)

    def is_editable(self) -> bool:
        """
        Returns whether the element is editable.
        :return:
        """
        return self.find.is_editable(timeout=self.timeout)

    def is_enabled(self) -> bool:
        """
        Returns whether the element is enabled.
        :return:
        """
        return self.find.is_enabled(timeout=self.timeout)

    def is_hidden(self) -> bool:
        """
        Returns whether the element is hidden, the opposite of visible.
        :return:
        """
        return self.find.is_hidden(timeout=self.timeout)

    def is_visible(self) -> bool:
        """
        Returns whether the element is visible.
        :return:
        """
        return self.find.is_visible(timeout=self.timeout)

    def screenshot(
            self,
            typo: Literal["jpeg", "png"] = None,
            path: Union[str, pathlib.Path] = None,
            quality: int = None,
            omit_background: bool = None,
            animations: Literal["allow", "disabled"] = None,
            caret: Literal["hide", "initial"] = None,
            scale: Literal["css", "device"] = None,
            mask: List["Locator"] = None,
    ) -> bytes:
        """
        This method captures a screenshot of the page
        :param typo:
        :param path:
        :param quality:
        :param omit_background:
        :param animations:
        :param caret:
        :param scale:
        :param mask:
        :return:
        """
        return self.find.screenshot(
            timeout=self.timeout,
            type=typo,
            path=path,
            quality=quality,
            omit_background=omit_background,
            animations=animations,
            caret=caret,
            scale=scale,
            mask=mask,
        )

    def scroll_into_view_if_needed(self) -> None:
        """
        This method waits for actionability checks, then tries to scroll element into view,
         unless it is completely visible as defined by IntersectionObserver's ratio.
        :return:
        """
        return self.find.scroll_into_view_if_needed(timeout=self.timeout)

    def wait_for(self, state: Literal["attached", "detached", "hidden", "visible"] = None) -> None:
        """
        Returns when element specified by locator satisfies the state option.
        :param state:
        :return:
        """
        return self.find.wait_for(
            timeout=self.timeout,
            state=state,
        )


class Locators:
    """
    Returns elements object
    """

    def __init__(
            self,
            selector: str,
            describe: str = "",
            position: Position = None,
            modifiers: List[KeyboardModifier] = None,
            delay: float = None,
            timeout: float = 1.0,
            force: bool = None,
            no_wait_after: bool = None,
            trial: bool = None,
            index: int = 0,
            has_context: bool = bool(False)):
        self.selector = selector
        self.desc = describe
        self.position = position
        self.modifiers = modifiers
        self.delay = delay
        self.timeout = timeout * 1000
        self.force = force
        self.no_wait_after = no_wait_after
        self.trial = trial
        self.index = index
        self.has_context = has_context

    def find(self, context):
        context.wait_for_load_state("load")
        elems = []
        for _ in range(3):
            try:
                elems = context.locator(self.selector).all()
                if len(elems) != 0:
                    break
            except Exception as e:
                logger.error(f"❌ {e}")
            time.sleep(self.timeout / 1000)
        for elem in elems:
            elem.evaluate('node => node.style.cssText="border:solid 2px blue"')
            time.sleep(0.02)
            elem.evaluate('node => node.style.cssText="border:solid 2px green"')
            time.sleep(0.02)
            elem.evaluate('node => node.style.cssText="border:solid 2px red"')
            time.sleep(0.01)
            elem.evaluate('node => node.style.cssText="border:solid 2px none"')

            if BrowserObject.playwright_screenshot_path:
                _auto_screenshot_with_playwright(elem=elem, driver=context, describe=self.desc)

        if self.desc == "":
            logger.info(f"✨ Find elements.")
        else:
            logger.info(f"✨ Find elements: {self.desc}.")
        return elems

    def __get__(self, instance, owner, context=None):
        if not instance:
            return None

        if not context and self.has_context:
            return lambda ctx: self.__get__(instance, owner, context=ctx)

        if not context:
            context = instance.page

        return self.find(context)

    def __set__(self, instance, value):
        elems = self.__get__(instance, instance.__class__)
        [elem.fill(value) for elem in elems]
