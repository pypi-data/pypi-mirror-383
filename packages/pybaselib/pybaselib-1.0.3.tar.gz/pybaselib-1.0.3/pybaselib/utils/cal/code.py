# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/9/25 13:16
import uuid

def generate_one_unique_code() -> str:
    """
    生成一个理论上唯一的16位十六进制字符串。

    该方法依赖于UUID4的强大随机性，在实践中几乎不可能重复。
    这是最高效、最常用的方法。

    Returns:
        一个16位的十六进制大写字符串。
    """
    # uuid.uuid4().hex 是32位，我们截取前16位
    return uuid.uuid4().hex[:16].upper()

if __name__ == '__main__':
    print(generate_one_unique_code())