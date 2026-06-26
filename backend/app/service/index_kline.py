"""指数 K 线 service — 编排 provider，组装前端所需结构。"""

from typing import Dict, List

from app.providers.index_kline import (
    SUPPORTED_INDICES,
    IndexKlineProvider,
)
from app.service.base_service import BaseService


class IndexKlineService(BaseService[Dict[str, object]]):
    """指数 K 线业务逻辑

    参数:
        symbol: 指数代码（H30269 / HSHYLV）
        period: 周期 day / week / month
        limit: 返回最近多少根 K 线
    """

    def __init__(self, symbol: str, period: str = "day", limit: int = 500):
        self.symbol = symbol
        self.period = period
        self.limit = limit

    async def _execute(self) -> Dict[str, object]:
        bars = await IndexKlineProvider(self.symbol, self.period, self.limit).get()
        return {
            "symbol": self.symbol,
            "name": SUPPORTED_INDICES.get(self.symbol, self.symbol),
            "period": self.period,
            "bars": bars,
        }


def list_supported_indices() -> List[Dict[str, str]]:
    """前端可选指数列表"""
    return [{"symbol": code, "name": name} for code, name in SUPPORTED_INDICES.items()]
