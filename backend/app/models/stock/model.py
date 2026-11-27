"""定义股票资料字段。"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StockInfo:
    symbol: str
    name: str
    exchange: str
    market: str
    currency: str = "CNY"
    price_tick: float = 0.01


@dataclass(frozen=True, slots=True)
class StockLookup:
    stock: StockInfo
    source: str
    source_version: str
    available_sources: tuple[str, ...]
    configured_sources: tuple[str, ...]
