from abc import ABC, abstractmethod
from typing import Any


class StockProvider(ABC):
    @abstractmethod
    async def get_daily(self, code: str, start: str, end: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def get_realtime(self, code: str) -> dict[str, Any]: ...
