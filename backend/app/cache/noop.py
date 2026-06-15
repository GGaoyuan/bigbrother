from typing import Any, Optional

from .base import BaseCache
from .policy import CachePolicy


class NoopCache(BaseCache):
    def is_fresh(self, key: str, policy: CachePolicy) -> bool:
        return False

    async def get(self, key: str) -> Optional[Any]:
        return None

    async def set(self, key: str, value: Any) -> None:
        pass


def get_cache() -> BaseCache:
    return NoopCache()
