from pathlib import Path
import os


def make_dir(path):
    """
    创建文件夹
    """
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print(f'{path} already exists')


class STATIC:
    def __init__(self):
        self.path = os.path.join(Path(__file__).parent.absolute().parent.parent, 'static')

class STATIC_DATAS:
    def __init__(self):
        self.path = os.path.join(STATIC().path, 'datas')
        make_dir(self.path)

class STATIC_DATAS_ETF:
    def __init__(self):
        self.path = os.path.join(STATIC_DATAS().path, 'ETF')
        make_dir(self.path)

class STATIC_DATAS_ETF_CSV:
    def __init__(self):
        self.path = os.path.join(STATIC_DATAS_ETF().path, 'csv')
        make_dir(self.path)
