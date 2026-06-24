"""全市场快照 provider — easy_tdx MacClient，不缓存。

数据源：通达信 Mac 行情协议（不经东财节点，稳定）
全市场约 5200 只，约 5 秒；不缓存（实时数据）
"""

import asyncio
from typing import List, Optional

from easy_tdx import Category
from pydantic import BaseModel

from app.cache import CacheTTL
from app.providers.client.easy_tdx_client import get_mac_client
from app.providers.base_provider import BaseProvider
from app.providers.cache_decorator import cached_json


class MarketQuote(BaseModel):
    """个股实时快照"""

    code: str
    name: str
    pre_close: Optional[float] = None  # 昨收
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None  # 现价
    change_pct: Optional[float] = None  # 涨跌幅（自算）
    volume: Optional[float] = None  # 成交量
    vol_ratio: Optional[float] = None  # 量比
    amount: Optional[float] = None  # 成交额
    turnover: Optional[float] = None  # 换手率


class MarketSnapshotProvider(BaseProvider[List[dict]]):
    """全市场快照数据源（沪深全部 A 股）"""

    async def _fetch(self) -> List[dict]:
        """从 easy_tdx 获取沪深全市场快照"""

        def _fetch_category(category: Category) -> list:
            client = get_mac_client()
            df = client.get_stock_quotes_list(category=category, count=10000)
            if df is None or df.empty:
                return []
            rows = []
            for _, row in df.iterrows():
                close = row.get("close")
                pre_close = row.get("pre_close")
                change_pct = None
                if close is not None and pre_close:
                    change_pct = round((close - pre_close) / pre_close * 100, 2)
                rows.append(
                    MarketQuote(
                        code=str(row.get("code", "")),
                        name=str(row.get("name", "")),
                        pre_close=float(pre_close) if pre_close is not None else None,
                        open=float(row["open"]) if row.get("open") is not None else None,
                        high=float(row["high"]) if row.get("high") is not None else None,
                        low=float(row["low"]) if row.get("low") is not None else None,
                        close=float(close) if close is not None else None,
                        change_pct=change_pct,
                        volume=float(row["vol"]) if row.get("vol") is not None else None,
                        vol_ratio=float(row["vol_ratio"]) if row.get("vol_ratio") is not None else None,
                        amount=float(row["amount"]) if row.get("amount") is not None else None,
                        turnover=float(row["turnover"]) if row.get("turnover") is not None else None,
                    ).model_dump()
                )
            return rows

        async def _do():
            sh, sz = await asyncio.gather(
                asyncio.to_thread(_fetch_category, Category.SH),
                asyncio.to_thread(_fetch_category, Category.SZ),
            )
            return sh + sz

        return await _do()

    @cached_json(namespace="market_snapshot", key="all", ttl=CacheTTL.NONE)
    async def get(self) -> List[dict]:
        """获取全市场快照（不缓存）"""
        return await self._fetch()
