import threading
import inspect
import time
import app.util.md5 as md5_util
from inspect import FrameInfo
#
# def select(time_interval: int = 60):
#     instance = CacherInstance()
#     instance.get_cache(time_interval)
#         # caller_name = Cacher.__get_caller()
#
#         # 根据时间间隔获取文件夹，默认是
#
#
# def update(json: str, time_interval: int = 60):
#     instance = CacherInstance()
#     instance.put(json, time_interval)
#
# class CacherInstance:
#     _instance = None
#     _lock = threading.Lock()  # 定义一个锁对象
#
#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             with cls._lock:  # 加锁，确保只有一个线程能够创建实例
#                 if not cls._instance:  # 双重检查，防止多次初始化
#                     cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def __init__(self):
#         pass
#
#     def put_cache(self, time_interval: int):
#         caller = self.__get_caller()
#         current_timestamp = int(time.time())
#
#     def get_cache(self, json: str, time_interval: int):
#         caller = self.__get_caller()
#         current_timestamp = int(time.time())
#
#     def __get_caller(self):
#         stack = inspect.stack()
#         func_info = stack[2]
#         file_name = func_info.filename
#         func_name = func_info.function
#         name = file_name + "_" + func_name
#         return md5_util.to_str(name)




###############################################################

# class Cacher:
#     # _instance = None
#     # _lock = threading.Lock()  # 锁对象，保证线程安全
#     #
#     # def __new__(cls, *args, **kwargs):
#     #     if not cls._instance:
#     #         with cls._lock:  # 加锁，防止多线程同时创建实例
#     #             if not cls._instance:
#     #                 cls._instance = super().__new__(cls)
#     #     return cls._instance
#
#     @staticmethod
#     def select(time_interval: int = 60):
#         caller_name = Cacher.__get_caller()
#         current_timestamp = int(time.time())
#         #根据时间间隔获取文件夹，默认是
#
#     @staticmethod
#     def update(value, time_interval: int = 60):
#         caller_name = Cacher.__get_caller()
#         current_timestamp = int(time.time())
#
#     @staticmethod
#     def __get_caller():
#         stack = inspect.stack()
#         func_info = stack[2]
#         file_name = func_info.filename
#         func_name = func_info.function
#         name = file_name + "_" + func_name
#         return md5_util.to_str(name)




#
# def singleton(cls):
#     instances = {}
#     def get_instance(*args, **kwargs):
#         if cls not in instances:
#             instances[cls] = cls(*args, **kwargs)
#         return instances[cls]
#     return get_instance
#
# @singleton
# class DaoCache(object):
#     def __init__(self):
#         self.__cache = {}
#
#     def __get_caller(self) -> str:
#         stack = inspect.stack()
#         func_info = stack[2]
#         file_name = func_info.filename
#         func_name = func_info.function
#         name = file_name + "_" + func_name
#         return md5_util.to_str(name)
#
#     def get(self):
#         caller = self.__get_caller()
#         if caller in self.__cache:
#             cache_obj = self.__cache[caller]
#             timestamp = cache_obj['timestamp']
#             # 获取时间
#             current_timestamp = int(time.time())
#             five_minutes_ago = current_timestamp - 5 * 60
#             # 在5分钟以内，且有数据
#             if five_minutes_ago <= timestamp <= current_timestamp and cache_obj['data'] is not None:
#                 print(f'{caller}成功获取数据！')
#                 return cache_obj['data']
#         return None
#
#     def set(self, value):
#         current_timestamp = int(time.time())
#         cache_obj = {
#             'timestamp': current_timestamp,
#             'data': value
#         }
#         caller = self.__get_caller()
#         self.__cache[caller] = cache_obj
#         print(f'{caller}已添加缓存')