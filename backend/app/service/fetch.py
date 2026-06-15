from typing import Awaitable, Callable, TypeVar

from app.cache.base import BaseCache
from app.cache.policy import CachePolicy

T = TypeVar("T")


async def with_cache(
    cache: BaseCache,
    key: str,
    policy: CachePolicy,
    fetcher: Callable[[], Awaitable[T]],
) -> T:
    """
    Service 层统一缓存入口。
    policy=NONE 时直接调 provider；否则按自然日/周/月边界判断缓存鲜度。
    """
    if policy == CachePolicy.NONE:
        return await fetcher()

    if cache.is_fresh(key, policy):
        cached = await cache.get(key)
        if cached is not None:
            return cached

    data = await fetcher()
    await cache.set(key, data)
    return data
