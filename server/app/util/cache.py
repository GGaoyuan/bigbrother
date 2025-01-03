from functools import wraps
from pathlib import Path
from enum import Enum
import inspect
import pandas as pd
import base64
import time

class Level(Enum):
    MINUTE1 = '60'
    MINUTE15 = '900'
    MINUTE30 = '1800'
    HOUR1 = '3600'
    HOUR3 = '10800'
    HOUR6 = '21600'
    HOUR12 = '43200'
    DAY = '86400'
    WEEK = '604800'



import threading

class PathSingleton:
    _instance = None
    _lock = threading.Lock()  # 创建一个锁
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:  # 锁定代码块
                if not cls._instance:
                    cls._instance = super(PathSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.cache_folder = Path.joinpath(Path(__file__).parent.absolute().parent.parent.parent).joinpath('static/cache')
        self.interval_folder = Path(self.cache_folder).joinpath('interval')
        for level in Level:
            sub_folder = self.interval_folder.joinpath(level.value)
            if not sub_folder.exists():
                sub_folder.mkdir(parents=True, exist_ok=True)
        print('PathSingleton build folder complete')

def cache(level: Level = Level.HOUR1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pathsingleton = PathSingleton()
            print("Something is happening before the function is called.")
            # 获取文件夹/文件
            func_name = func.__name__
            file_name = Path(inspect.getfile(func)).name
            class_name = 'none'
            if inspect.ismethod(func):
                class_name = func.__self__.__class__.__name__
            caller_info = ('file name = ' + file_name + '&' +
                           'class name = ' + class_name + '&' +
                           'func name = ' + func_name + '&' +
                           'args = ' + ('_'.join(str(arg) for arg in args)))
            caller_info_base64 = base64.b64encode(caller_info.encode('utf-8')).decode('utf-8')
            caller_folder_path = Path(pathsingleton.interval_folder).joinpath(level.value).joinpath(caller_info_base64)
            caller_folder_path.mkdir(parents=True, exist_ok=True)
            # 获取数据
            files = [file for file in caller_folder_path.iterdir() if file.is_file()]
            file = None
            current_timestamp = int(time.time())
            if len(files) > 0:
                file = files[0]
                cache_timestamp = Path(file).stem
                limit_timestamp = current_timestamp - int(level.value)
                if limit_timestamp > int(cache_timestamp):
                    Path(file).unlink()
                    file = None
            if file is None:
                print(f"cache:网络拉取 {func_name}")
                result = func(*args, **kwargs)
                if type(result) is pd.DataFrame:
                    df = pd.DataFrame(result)
                    df.to_csv(caller_folder_path.joinpath(str(current_timestamp) + '.csv'))
            else:
                print(f"cache:获取缓存 {func_name}")
                result = pd.read_csv(file)
            return result
        return wrapper
    return decorator
