import sys
import os
# 将项目根目录添加到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import re
import pytest


# 定义一个 fixture，用于前置条件
@pytest.fixture
def setup_data():
    print("前置条件：初始化数据")
    data = {"name": "test", "value": 42}
    yield data  # yield 前是前置逻辑，yield 后是后置逻辑
    print("后置条件：清理数据")

# 使用 fixture 的测试用例
def test_example(setup_data):
    print(f"测试数据：{setup_data}")


    assert setup_data["value"] == 42

@pytest.fixture(autouse=True)
def auto_setup():
    print("自动前置条件：所有测试用例都会执行此 fixture")



@pytest.fixture
def data():
    return [1, 2, 3]

def test_sum(data):
    assert sum(data) == 6