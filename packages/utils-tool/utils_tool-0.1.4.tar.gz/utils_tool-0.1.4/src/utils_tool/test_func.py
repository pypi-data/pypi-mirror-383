

"""抓包和反编译 pyshark"""

import time
import pyshark
import functools
from itertools import islice




# !pip install pyshark
# 使用过滤器捕获 HTTP 流量
capture = pyshark.LiveCapture(interface="Wi-Fi", display_filter="http")

# 捕获流量，设置超时时间为50秒
capture.sniff(timeout=5)

# 打印捕获到的 HTTP 数据包
print("start")
for packet in capture:
    print(packet)
    # print('Packet Number:', packet.number)
    # print('Timestamp:', packet.sniff_time)
    # print('Source IP:', packet.ip.src)
    # print('Destination IP:', packet.ip.dst)
    time.sleep(0.1)


# 捕获网络接口上的流量
capture = pyshark.LiveCapture(interface="eth0")

# 捕获流量，设置超时时间为50秒
capture.sniff(timeout=50)

# 访问数据包内容
for packet in capture:
    print("Packet Number:", packet.number)
    print("Timestamp:", packet.sniff_time)
    print("Source IP:", packet.ip.src)
    print("Destination IP:", packet.ip.dst)
    if "http" in packet:
        print("HTTP Method:", packet.http.request_method)
        print("HTTP Host:", packet.http.host)



## locust 压力测试


def struct():
    """
    一个装饰器，用于在运行时校验函数的输入参数和返回值的类型。

    此装饰器通过检查函数注解来确保传入的参数类型和函数返回值的类型符合预期。
    如果类型不匹配，将抛出 AssertionError。

    推荐在工程化项目中使用，以增强代码的健壮性和可维护性。

    用法示例:
        >>> @struct()
        >>> def add(a: int, b: int) -> int:
        >>>     return a + b
        >>> add(1, 2) # 正常执行
        3
        >>> add(1, "2") # 抛出 AssertionError

    Returns:
        Callable: 一个包装函数，用于执行类型校验。
    """

    def outer_packing(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            ann_dict = func.__annotations__

            if len(args) != 0:
                remaining_items = islice(ann_dict.items(), None, len(args))
                args_result_dict = dict(remaining_items)
                args_result_list = list(args_result_dict.values())
                try:
                    for i, j in enumerate(args_result_list):
                        assert isinstance(args[i], j)
                except AssertionError as e:
                    raise AssertionError(f"位置: {i} 预期的输入是: {j}") from e

            try:
                for k, v in kwargs.items():
                    assert isinstance(v, ann_dict[k])
            except AssertionError as e:
                raise AssertionError(f"位置: {k} 预期的输入是: {v}") from e
            try:
                assert isinstance(result, ann_dict.get("return", object))
            except AssertionError as e:
                raise AssertionError("返回值格式不准确") from e

            return result

        return wrapper

    return outer_packing

