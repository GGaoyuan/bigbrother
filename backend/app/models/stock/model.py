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
