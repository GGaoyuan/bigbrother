from pathlib import Path
import os




def folder_datas() -> str:
    """
    获取datas文件夹
    """
    static_path = os.path.join(Path(__file__).parent.absolute().parent.parent, 'static')
    data_path = os.path.join(static_path, 'datas')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    return data_path

def folder_etf() -> str:
    pass


def __test():
    pass