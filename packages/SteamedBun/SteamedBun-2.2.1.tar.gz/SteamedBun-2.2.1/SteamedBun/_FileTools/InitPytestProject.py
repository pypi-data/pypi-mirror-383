"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: InitPytestProject.py
@Time: 2025/10/7 23:46
"""
import argparse
import sys
from pathlib import Path

__version__ = "1.0.0"


def create_pytest_project(project_name="my_pytest_project"):
    """
    创建pytest项目的基础结构

    Args:
        project_name: 项目名称，默认是"my_pytest_project"
    """
    # 创建项目根目录
    project_root = Path(project_name)
    project_root.mkdir(exist_ok=True)
    print(f"创建项目根目录: {project_root}")

    # 创建apis目录及示例模块
    apis_dir = project_root / "apis"
    apis_dir.mkdir(exist_ok=True)

    # 创建apis/__init__.py
    (apis_dir / "__init__.py").touch()

    # 创建示例模块1
    api_v1_dir = apis_dir / "api_v1"
    api_v1_dir.mkdir(exist_ok=True)
    (api_v1_dir / "__init__.py").touch()

    # 写入示例业务代码
    api_v1 = api_v1_dir / "api_v1.py"
    with open(api_v1, "w", encoding="utf-8") as f:
        f.write("""def add(a: int, b: int) -> int:
    \"\"\"两数相加\"\"\"
    return a + b


def multiply(a: int, b: int) -> int:
    \"\"\"两数相乘\"\"\"
    return a * b
""")
    print(f"创建业务代码文件: {api_v1}")

    # 创建示例模块2
    api_v2_dir = apis_dir / "api_v2"
    api_v2_dir.mkdir(exist_ok=True)
    (api_v2_dir / "__init__.py").touch()

    # 写入示例工具函数
    utils_py = api_v2_dir / "utils.py"
    with open(utils_py, "w", encoding="utf-8") as f:
        f.write("""def is_positive(number: int) -> bool:
    \"\"\"判断一个数是否为正数\"\"\"
    return number > 0


def to_upper(text: str) -> str:
    \"\"\"将字符串转换为大写\"\"\"
    return text.upper()
""")
    print(f"创建业务代码文件: {utils_py}")

    # 创建cases目录及结构
    cases_dir = project_root / "cases"
    cases_dir.mkdir(exist_ok=True)
    (cases_dir / "__init__.py").touch()

    # 创建conftest.py
    conftest_py = cases_dir / "conftest.py"
    with open(conftest_py, "w", encoding="utf-8") as f:
        f.write("""from SteamedBun import fixture


@fixture(scope="module")
def sample_data():
    \"\"\"提供测试用的示例数据\"\"\"
    return {
        "numbers": [1, 2, 3, 4, 5],
        "strings": ["hello", "world", "pytest"]
    }
""")
    print(f"创建配置文件: {conftest_py}")

    # 创建pytest.ini配置文件
    pytest_ini = project_root / "pytest.ini"
    with open(pytest_ini, "w", encoding="utf-8") as f:
        f.write("""[pytest]
testpaths = cases
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --color=yes
""")
    print(f"创建配置文件: {pytest_ini}")

    # 创建测试模块1的测试代码
    test_api_v1_dir = cases_dir / "test_api_v1"
    test_api_v1_dir.mkdir(exist_ok=True)
    (test_api_v1_dir / "__init__.py").touch()

    test_api_v1 = test_api_v1_dir / "test_api_v1.py"
    with open(test_api_v1, "w", encoding="utf-8") as f:
        f.write("""from apis.api_v1.api_v1 import add, multiply


def test_add(sample_data):
    \"\"\"测试加法函数\"\"\"
    # 测试正常情况
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

    # 使用fixture提供的数据测试
    nums = sample_data["numbers"]
    assert add(nums[0], nums[1]) == nums[0] + nums[1]


def test_multiply():
    \"\"\"测试乘法函数\"\"\"
    assert multiply(3, 4) == 12
    assert multiply(-2, 5) == -10
    assert multiply(0, 100) == 0
""")
    print(f"创建测试文件: {test_api_v1}")

    # 创建测试模块2的测试代码
    test_api_v2_dir = cases_dir / "test_api_v2"
    test_api_v2_dir.mkdir(exist_ok=True)
    (test_api_v2_dir / "__init__.py").touch()

    test_utils_py = test_api_v2_dir / "test_utils.py"
    with open(test_utils_py, "w", encoding="utf-8") as f:
        f.write("""from apis.api_v2.utils import is_positive, to_upper


def test_is_positive():
    \"\"\"测试判断正数的函数\"\"\"
    assert is_positive(5) is True
    assert is_positive(-3) is False
    assert is_positive(0) is False


def test_to_upper(sample_data):
    \"\"\"测试字符串转大写函数\"\"\"
    assert to_upper("hello") == "HELLO"
    assert to_upper("PyTest") == "PYTEST"

    # 使用fixture提供的数据测试
    for s in sample_data["strings"]:
        assert to_upper(s) == s.upper()
""")
    print(f"创建测试文件: {test_utils_py}")

    # 创建requirements.txt
    requirements_txt = project_root / "requirements.txt"
    with open(requirements_txt, "w", encoding="utf-8") as f:
        f.write("""SteamedBun
""")
    print(f"创建依赖文件: {requirements_txt}")

    # 创建.gitignore
    gitignore = project_root / ".gitignore"
    with open(gitignore, "w", encoding="utf-8") as f:
        f.write("""# Python字节码
__pycache__/
*.py[cod]
*$py.class

# 虚拟环境
venv/
env/
*.env

# 测试报告
*.html
.pytest_cache/

# 操作系统文件
.DS_Store
Thumbs.db

# 编辑器文件
.idea/
.vscode/
*.swp
*.swo
""")
    print(f"创建忽略文件: {gitignore}")

    print("\n项目初始化完成！")
    print(f"项目路径: {project_root.absolute()}")
    print("接下来可以执行以下命令:")
    print(f"cd {project_name}")
    print("python -m venv venv")
    print("source venv/bin/activate  # Linux/Mac")
    print("venv\\Scripts\\activate     # Windows")
    print("pip install -r requirements.txt")
    print("pytest  # 运行所有测试")
    print("pytest --html=report.html  # 生成HTML测试报告")


def create_project_tool():
    # 自定义错误处理类
    class CustomArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            # 打印用法信息和描述
            self.print_usage()
            print()
            print(self.description)
            print()
            # 打印位置参数信息
            print("positional arguments:")
            print("  {create}")
            print("    create    创建项目")
            print()
            # 打印可选参数信息
            print("optional arguments:")
            print("  -h, --help  show this help message and exit")
            # 退出程序
            sys.exit(2)

    # 使用自定义解析器
    parser = CustomArgumentParser(description="初始化pytest项目结构, 使用示例: cpt my_pytest_project")

    # 将name设置为位置参数，并指定默认值
    parser.add_argument(
        "name",
        default="my_pytest_project",
        help="项目名称（例如：my_pytest_project）"
    )

    # 解析参数
    args = parser.parse_args()

    # 使用参数创建项目
    create_pytest_project(args.name)
