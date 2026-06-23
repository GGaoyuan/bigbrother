"""Provider 层缓存装饰器 — 让每个 provider 方法自己决定缓存策略。

使用方式：
    @cached_json(key="limit_up_pool", ttl=CacheTTL.HOURLY)
    async def get_limit_up_pool() -> List[LimitStock]:
        # 数据获取逻辑
        ...

    # 带参数的 key（用占位符）
    @cached_json(key="limit_up_pool_{date}", ttl=CacheTTL.HOURLY)
    async def get_limit_up_pool(date: str) -> List[LimitStock]:
        # key 自动替换 {date} 为实参
        ...

特性：
- 自动从函数参数构建缓存 key（占位符替换）
- 缓存命中时直接返回，不执行函数体
- 异常不缓存（失败不污染缓存）
"""

import functools
from typing import Any, Callable, TypeVar

from app.cache import CacheTTL, json_cache

T = TypeVar("T")


def cached_json(key: str, ttl: CacheTTL) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """JSON 缓存装饰器（provider 层专用）

    Args:
        key: 缓存键，支持占位符 {param_name} 从函数参数取值
        ttl: 缓存时长

    Example:
        @cached_json(key="stock_{code}", ttl=CacheTTL.DAILY)
        async def get_stock(code: str):
            return fetch_data(code)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # 构建缓存 key（占位符替换）
            import inspect

            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = bound.arguments

            # 替换占位符
            cache_key = key
            for param, value in params.items():
                placeholder = f"{{{param}}}"
                if placeholder in cache_key:
                    cache_key = cache_key.replace(placeholder, str(value or ""))

            # 尝试从缓存读取
            cached = await json_cache.get(cache_key)
            if cached is not None:
                return cached

            # 执行函数
            result = await func(*args, **kwargs)

            # 写入缓存（仅成功时）
            await json_cache.set(cache_key, result, ttl=ttl)
            return result

        return wrapper

    return decorator
