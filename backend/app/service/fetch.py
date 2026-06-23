from typing import Awaitable, Callable, List, TypeVar

from app.cache import CacheTTL, csv_cache, json_cache

T = TypeVar("T")


async def with_json_cache(
    key: str,
    ttl: CacheTTL,
    fetcher: Callable[[], Awaitable[T]],
) -> T:
    """JSON 缓存包装：命中即返回，未命中调 fetcher 并写回 json_cache。"""
    cached = await json_cache.get(key)
    if cached is not None:
        return cached
    value = await fetcher()
    await json_cache.set(key, value, ttl=ttl)
    return value


async def with_csv_cache(
    key: str,
    ttl: CacheTTL,
    fetcher: Callable[[], Awaitable[List[dict]]],
) -> List[dict]:
    """CSV 缓存包装：命中即返回行集合，未命中调 fetcher 并写回 csv_cache。"""
    cached = await csv_cache.get(key)
    if cached is not None:
        return cached
    rows = await fetcher()
    await csv_cache.set(key, rows, ttl=ttl)
    return rows
