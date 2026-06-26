"""指数 K 线 provider — easy_tdx MacClient 数据源，不缓存。

数据源选择：
- 使用 easy_tdx MacClient（Mac 行情协议，稳定快速）
- 通过 get_stock_kline 获取指数数据

周期映射：day / week / month -> Period
"""

import asyncio
from typing import List

import pandas as pd
from easy_tdx import Period

from app.base.safe_value import safe_float, safe_str
from app.providers.base_provider import BaseProvider
from app.providers.cache_decorator import CacheTTL, cached_json
from app.providers.client.easy_tdx_client import get_mac_client
from app.providers.model.index_kline import IndexKlineBar

# 前端展示的指数：代码 -> 名称
SUPPORTED_INDICES = {
    "H30269": "红利低波",
    "HSHYLV": "恒生港股通高股息低波动",
}

# 前端代码 -> TDX 市场号和代码
#
# 注意：中证策略指数（H30269 / HSHYLV，TDX 内对应 931468 / 931373）TDX 行情协议
# 不收录，easy_tdx / mootdx 均取不到。改用跟踪 ETF 代理：
#   H30269 红利低波            -> 563020 低波红利ETF易方达（沪）
#   HSHYLV 恒生港股通高股息低波动 -> 159545 港股红利低波ETF易方达（深）
_SYMBOL_MAP = {
    "H30269": (1, "563020"),  # (上海市场, 低波红利ETF易方达)
    "HSHYLV": (0, "159545"),  # (深圳市场, 港股红利低波ETF易方达)
}

# 周期字符串 -> Period 枚举
_PERIOD_MAP = {
    "day": Period.DAILY,
    "week": Period.WEEKLY,
    "month": Period.MONTHLY,
}


class IndexKlineProvider(BaseProvider[List[dict]]):
    """指数 K 线数据源（easy_tdx MacClient）

    参数:
        symbol: 指数代码，如 H30269 / HSHYLV
        period: 周期，day(日线) / week(周线) / month(月线)
        limit: 返回最近多少根 K 线
    """

    def __init__(self, symbol: str, period: str = "day", limit: int = 500):
        self.symbol = symbol
        self.period = period if period in _PERIOD_MAP else "day"
        self.limit = limit

    async def _fetch(self) -> List[dict]:
        """从 easy_tdx MacClient 获取指数 K 线"""

        def _do():
            # 获取市场号和代码
            market_info = _SYMBOL_MAP.get(self.symbol)
            if not market_info:
                return []

            market, code = market_info
            period = _PERIOD_MAP[self.period]

            # 使用复用的 MacClient
            client = get_mac_client()
            df = client.get_stock_kline(
                market=market,
                code=code,
                period=period,
                start=0,
                count=self.limit
            )

            if df is None or df.empty:
                return []

            return self._convert_to_bars(df)

        return await asyncio.to_thread(_do)

    def _convert_to_bars(self, df: pd.DataFrame) -> List[dict]:
        """转换数据格式"""
        bars: List[IndexKlineBar] = []
        for _, row in df.iterrows():
            bars.append(
                IndexKlineBar(
                    trade_date=safe_str(row.get("datetime", ""))[:10],
                    open=safe_float(row.get("open", 0)),
                    high=safe_float(row.get("high", 0)),
                    low=safe_float(row.get("low", 0)),
                    close=safe_float(row.get("close", 0)),
                    volume=safe_float(row.get("vol", 0)),
                    amount=safe_float(row.get("amount", 0)),
                    change_pct=0.0,
                )
            )

        # 计算涨跌幅
        for i in range(1, len(bars)):
            if bars[i - 1].close > 0:
                bars[i].change_pct = (
                    (bars[i].close - bars[i - 1].close) / bars[i - 1].close * 100
                )

        return [b.model_dump() for b in bars]

    @cached_json(namespace="index_kline", key="{self.symbol}_{self.period}", ttl=CacheTTL.NONE)
    async def get(self) -> List[dict]:
        """获取指数 K 线（不缓存）"""
        return await self._fetch()
