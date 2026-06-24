"""Provider 层缓存装饰器 — 让每个 provider 方法自己决定缓存策略。

默认不缓存：provider 方法不加装饰器即可（直接返回原始数据）。
需要缓存时再加 @cached_json，且必须指定 namespace（缓存子目录），
不同 provider 用不同 namespace 隔离缓存文件。

使用方式：
    @cached_json(namespace="limit_pool", key="limit_up_{date}", ttl=CacheTTL.HOURLY)
    async def get(self, date: str) -> List[dict]:
        ...

特性：
- 缓存文件落在 data/<namespace>/ 子目录下
- 自动从函数参数构建缓存 key（占位符替换）
- 缓存命中时直接返回，不执行函数体
- 异常不缓存（失败不污染缓存）
"""

import functools
from typing import Callable, TypeVar

from app.cache import CacheTTL, json_cache

T = TypeVar("T")


def cached_json(
    namespace: str, key: str, ttl: CacheTTL
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """JSON 缓存装饰器（provider 层专用）

    Args:
        namespace: 缓存子目录名（不同 provider 用不同 namespace 隔离）
        key: 缓存键，支持占位符 {param_name} 从函数参数取值
        ttl: 缓存时长

    Example:
        @cached_json(namespace="limit_pool", key="limit_up_{date}", ttl=CacheTTL.HOURLY)
        async def get(self, date: str):
            return fetch_data(date)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # ttl=NONE 时完全跳过缓存读写，直接执行
            if ttl == CacheTTL.NONE:
                return await func(*args, **kwargs)

            # 构建缓存 key（占位符替换）
            import inspect

            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = dict(bound.arguments)

            # 若是实例方法，把 self 的属性也纳入占位符取值范围
            # （支持 key 用 {date} 取 self.date 这类实例属性）
            self_obj = params.pop("self", None)
            placeholder_values = dict(params)
            if self_obj is not None:
                for attr in vars(self_obj):
                    placeholder_values.setdefault(attr, getattr(self_obj, attr))

            # 替换占位符
            cache_key = key
            for name, value in placeholder_values.items():
                placeholder = f"{{{name}}}"
                if placeholder in cache_key:
                    cache_key = cache_key.replace(placeholder, str(value or ""))

            # 尝试从缓存读取（在 namespace 子目录下）
            cached = await json_cache.get(cache_key, namespace=namespace)
            if cached is not None:
                return cached

            # 执行函数
            result = await func(*args, **kwargs)

            # 写入缓存（仅成功时）
            await json_cache.set(cache_key, result, ttl=ttl, namespace=namespace)
            return result

        return wrapper

    return decorator
