from typing import Any, Optional
from .base import BaseCache


class NoopCache(BaseCache):
    async def get(self, key: str) -> Optional[Any]:
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass


def get_cache() -> BaseCache:
    return NoopCache()
