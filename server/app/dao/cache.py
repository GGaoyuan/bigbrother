import inspect
import time


def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class DaoCache(object):
    def __init__(self):
        self.__cache = {}

    def __get_caller(self) -> str:
        return inspect.stack()[1][3]

    def get(self):
        caller = self.__get_caller()
        if caller in self.__cache:
            cache_obj = self.__cache[caller]
            timestamp = cache_obj['timestamp']
            # 获取时间
            current_timestamp = int(time.time())
            five_minutes_ago = current_timestamp - 5 * 60
            # 在5分钟以内，且有数据
            if five_minutes_ago <= timestamp <= current_timestamp and cache_obj['data'] is not None:
                print(f'{caller}成功获取数据！')
                return cache_obj['data']
        return None

    def set(self, value):
        current_timestamp = int(time.time())
        cache_obj = {
            'timestamp': current_timestamp,
            'data': value
        }
        caller = self.__get_caller()
        self.__cache[caller] = cache_obj
        print(f'{caller}已添加缓存')