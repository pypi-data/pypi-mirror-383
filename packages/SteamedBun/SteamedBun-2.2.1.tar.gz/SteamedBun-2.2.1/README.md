###### ✅ create pytest project 创建pytest自动化框架项目
```shell

cpt my_pytest_project

# 执行上述命令后, 根据后续指令配置项目环境即可
```



###### ✅ write excel 写多个Sheet表单示例

```python
from SteamedBun import FileOperate
from SteamedBun import FileNames

FileOperate.write_excel_with_many_sheets(
    filename=FileNames.ExcelFile,
    data={
        "sheet1": {
            "A列": ["a", "b", "c"],
            "B列": ["1", "2", "3"]
        },
        "sheet2": {
            "学科": ["en", "cn", "mt"],
            "分数": [30, 80, 70]
        }
    }
)

```

###### ✅ quote 毒鸡汤语录

```python
from SteamedBun import QuoteFormat

quote = QuoteFormat.random_quote()
print(quote)
```

###### ✅ selenium WAP 自动化示例

```python
from SteamedBun import Browser

driver = Browser(headless=False, wap=True, width=476, height=776)
driver.get("https://www.example.com")
driver.find_element("id", "id_v1").send_keys("馒头")
driver.close()
```

###### ✅ 原始mysql工具类示例

```python
from SteamedBun import MySQL

with MySQL() as db:
    print(db.query())

```

###### ✅ 自定义级别日志示例

```python
from SteamedBun import logger

logger.step(msg="这是自定义级别的日志")
# 上述将输出以下内容: 
# 2024-10-09 22:27:34,510 | tmp.py | 8 | STEP | 这是自定义级别的日志 

```

###### ✅ playwright 自动化示例

```python
from SteamedBun import playwright, Locator, Locators
from playwright.sync_api import sync_playwright


class PypiPage(playwright.Page):
    pypi_url = "https://pypi.org/"
    search_input = Locator(selector="[id='search']", describe="搜索框")
    search_btn = Locator(selector="form > button", describe="搜索按钮")
    txt = Locators(selector="//*[text()='三方库']", describe="随机文案")


with sync_playwright().start().chromium.launch(headless=False) as browser:
    driver = browser.new_page()
    page = PypiPage(page=driver)
    page.goto(page.pypi_url)
    page.search_input.send_keywords(value="SteamedBun")
    # page.search_input.send_keywords(value="SteamedBun", enter=True)
    # page.search_input.send_keyboards(key="Enter")
    page.search_btn.click()
    print([each.inner_text() for each in page.txt])
    # page.sleep()
    # page.screenshot()
    # page.close()

```

###### ✅ 提供指定元素组件 截图功能 + UI自动化识别动态验证码功能

```python
from SteamedBun import Browser
from SteamedBun import Element
from SteamedBun import OcrFormat
from SteamedBun import Page
from SteamedBun import case_title
from SteamedBun import case_step


class QuotePage(Page):
    """
    古诗词网站 登录页面元素
    """
    example_url = "https://so.gushiwen.cn/user/login.aspx"
    img_code = Element(id_="imgCode", describe="动态验证码")


@case_title(title="识别动态验证码")
def test_ocr_dynamic_code():
    with case_step("进入古诗词网站"):
        driver = Browser()
        page = QuotePage(driver=driver)
        page.open(page.example_url)

    with case_step("截图 指定的组件"):
        img_name = "img_code.png"
        page.img_code.screenshots(filename=img_name)

    with case_step("ocr 识别 截图中的验证码"):
        code = OcrFormat.ocr_word(filename=img_name)  # 若不可用, 手动去下载ddddocr库 替换该方法
        print(f"code: {code}")

```

###### ✅ 提供priority 优先级装饰器

```python
from SteamedBun import case_priority


@case_priority(order=2)
def test_01():
    pass


@case_priority(order=1)
def test_02():
    pass
```

###### ✅ 新增http请求 日志打印开关

```python
from SteamedBun import get

get("https://www.baidu.com", show=False)
```

###### ✅ UI驱动工具 - 提供持久态可复用的浏览器窗口

```python
from SteamedBun import Browser
from SteamedBun import Element
from SteamedBun import Page


class BaiDuPage(Page):
    example_url = "https://baidu.com"
    input_search = Element(id_="kw")


def test_chrome_browser():
    # browser_type 可以指定浏览器类型, 若不指定 默认就是Chrome
    driver = Browser(browser_type="chrome")
    page = BaiDuPage(driver=driver)
    page.open(page.example_url)
    page.input_search.send_keys("321")

```

###### ✅ 全局配置工具 - 支持读写ini类型文件、初始化运行环境

```python

from SteamedBun import set_env_by_file, SetEnvironment, set_env

set_env_by_file(env_path="conf.ini")
# 或者
SetEnvironment(env_path="conf.ini")
# 或者
set_env(env="test")

```

###### ✅ 装饰器 - 数据驱动装饰、用例描述修饰器

```python
from SteamedBun import param_file, case_title


@param_file("测试数据文件")
@case_title("用例标题")
def test_example(param):
    print(param)
```

###### ✅ 日志打印工具

```python
from SteamedBun import logger
from SteamedBun import FileNames

# 默认打印INFO级别的日志至控制台
logger.info("info")

# 打印DEBUG级别的日志至文件, 仍受限于全局的日志等级: 实际仍然打印INFO级别的
logger.setFilename(filename=FileNames.LogFile, level="DEBUG")

logger.warning("warning")

# 设置全局的日志打印等级
logger.setLevel(level="DEBUG")

```

###### ✅ 时间回溯工具

```python

from SteamedBun import TimeFormat

dt1 = TimeFormat.flash_back(days=-1)
print(f"往前回溯了一天: {dt1}")

dt2 = TimeFormat.flash_back(month=1)
print(f"往后穿越一个月: {dt2}")

print(dt2 < dt1)  # True
```

###### ✅ 文件处理工具

```python
from SteamedBun import FileOperate

# 设置jsonify 可以转换为json格式, 反之为字符串
FileOperate.read_file(filename="some.json", jsonify=True)
FileOperate.read_excel(filename="some.xlsx", sheet_name="Sheet1")

# 写入文件
FileOperate.write_file(filename="some.json", data="{}")
FileOperate.write_excel(
    filename="some.xlsx",
    data={"a列头": [1, 2, 3], "b列头": ["a", "b", "c"]}
)

```