from abc import ABC, abstractmethod
from typing import Any, Optional

from .policy import CachePolicy


class BaseCache(ABC):
    @abstractmethod
    def is_fresh(self, key: str, policy: CachePolicy) -> bool: ...

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]: ...

    @abstractmethod
    async def set(self, key: str, value: Any) -> None: ...
