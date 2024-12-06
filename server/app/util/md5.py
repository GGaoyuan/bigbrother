import hashlib
import json
def to_str(input) -> str:
    """
    md5计算
    :param input:
    :return:
    """
    # 对于复杂类型（如列表、字典等），使用 json.dumps 进行转换
    if isinstance(input, (list, dict)):
        input_str = json.dumps(input, sort_keys=True)
    elif isinstance(input, str):
        input_str = input
    else:
        input_str = str(input)
    # 创建 md5 对象
    md5_obj = hashlib.md5()
    # 将字符串编码为字节，然后更新 md5 对象
    md5_obj.update(input_str.encode('utf-8'))
    # 获取 16 进制的 md5 值
    md5_value = md5_obj.hexdigest()
    return md5_value
