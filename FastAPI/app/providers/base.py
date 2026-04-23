from abc import ABC, abstractmethod
from typing import Any


class StockProvider(ABC):
    @abstractmethod
    async def get_daily(self, code: str, start: str, end: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def get_realtime(self, code: str) -> dict[str, Any]: ...

    @abstractmethod
    async def get_market_stats(self, date: str) -> dict[str, Any]:
        """
        获取市场统计数据

        返回字段：
        - up_count: 上涨数量
        - down_count: 下跌数量
        - limit_up_count: 涨停数量
        - limit_down_count: 跌停数量
        - avg_change_pct: 平均涨跌幅
        - total_volume: 总成交额（元）
        - max_change_pct: 最大涨幅
        """
        ...
