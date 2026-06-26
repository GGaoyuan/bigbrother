"""成交量分布 K 线 provider — easy_tdx MacClient，按 PRD 要求不做缓存。

数据源：通达信 Mac 行情协议（直连，稳定，分钟线/日线齐全）。
周期支持：1m / 5m / 30m / day（成交量分布用）。

性能：单次 get_stock_kline 调用即可取够区间，走线程池避免阻塞事件循环；
不加缓存（实时性优先，PRD 明确要求）。
"""

import asyncio
from typing import List

from easy_tdx import Period

from app.base.safe_value import safe_float
from app.providers.base_provider import BaseProvider
from app.providers.cache_decorator import CacheTTL, cached_json
from app.providers.client.easy_tdx_client import get_mac_client
from app.providers.model.volume_kline import VolumeKlineBar

# 周期字符串 -> easy_tdx Period 枚举
_PERIOD_MAP = {
    "1m": Period.MIN_1,
    "5m": Period.MIN_5,
    "30m": Period.MIN_30,
    "day": Period.DAILY,
}

# 分钟级周期：datetime 需保留到 HH:MM
_MINUTE_PERIODS = {"1m", "5m", "30m"}


def resolve_market(symbol: str) -> int:
    """根据 6 位证券代码推断 easy_tdx 市场号（0=深市，1=沪市）。

    symbol: 6 位证券代码，如 600519 / 000001 / 688981。
    """
    code = symbol.strip()
    # 沪市：6 开头（主板/科创板 688）、9 开头（B 股）、5 开头（基金）
    if code.startswith(("6", "9", "5")):
        return 1
    # 深市：0 / 3（创业板）/ 1（深市基金/债）
    return 0


class VolumeKlineProvider(BaseProvider[List[dict]]):
    """成交量分布 K 线数据源（easy_tdx，无缓存）

    参数:
        symbol: 6 位证券代码，如 600519
        period: 周期 1m / 5m / 30m / day
        count: 返回最近多少根 K 线
    """

    def __init__(self, symbol: str, period: str = "day", count: int = 300):
        self.symbol = symbol
        self.period = period if period in _PERIOD_MAP else "day"
        self.count = count

    async def _fetch(self) -> List[dict]:
        """从 easy_tdx 获取 K 线（含成交量）"""

        def _do():
            client = get_mac_client()
            market = resolve_market(self.symbol)
            period = _PERIOD_MAP[self.period]
            df = client.get_stock_kline(
                market, self.symbol, period=period, count=self.count
            )
            if df is None or df.empty:
                return []
            keep_time = self.period in _MINUTE_PERIODS
            bars: List[VolumeKlineBar] = []
            for _, row in df.iterrows():
                raw_dt = row.get("datetime")
                if raw_dt is None:
                    dt = None
                elif keep_time:
                    dt = str(raw_dt)[:16]  # YYYY-MM-DD HH:MM
                else:
                    dt = str(raw_dt)[:10]  # YYYY-MM-DD
                bars.append(
                    VolumeKlineBar(
                        datetime=dt,
                        open=safe_float(row.get("open")),
                        high=safe_float(row.get("high")),
                        low=safe_float(row.get("low")),
                        close=safe_float(row.get("close")),
                        volume=safe_float(row.get("vol")),
                        amount=safe_float(row.get("amount")),
                    )
                )
            return [b.model_dump() for b in bars]

        return await asyncio.to_thread(_do)

    @cached_json(namespace="volume_kline", key="{self.symbol}_{self.period}", ttl=CacheTTL.NONE)
    async def get(self) -> List[dict]:
        """获取 K 线（不缓存，实时取数）"""
        return await self._fetch()
