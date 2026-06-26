"""成交量分布 K 线 service — 编排 provider，组装前端结构。"""

from typing import Dict

from app.providers.volume_kline import VolumeKlineProvider
from app.service.base_service import BaseService


class VolumeKlineService(BaseService[Dict[str, object]]):
    """成交量分布 K 线业务逻辑

    参数:
        symbol: 6 位证券代码
        period: 周期 1m / 5m / 30m / day
        count: 返回最近多少根 K 线
    """

    def __init__(self, symbol: str, period: str = "day", count: int = 300):
        self.symbol = symbol
        self.period = period
        self.count = count

    async def _execute(self) -> Dict[str, object]:
        bars = await VolumeKlineProvider(self.symbol, self.period, self.count).get()
        return {
            "symbol": self.symbol,
            "period": self.period,
            "bars": bars,
        }
