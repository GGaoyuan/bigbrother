"""涨跌停池 provider（完全符合 BaseProvider 规范）

数据源：akshare 东财涨跌停池接口（稳定）
不缓存：ttl=CacheTTL.NONE（需要缓存时改 ttl 即可）
"""

import asyncio
from datetime import datetime
from typing import List, Optional

import akshare as ak
from pydantic import BaseModel

from app.cache import CacheTTL
from app.providers.base_provider import BaseProvider
from app.providers.cache_decorator import cached_json


class LimitStock(BaseModel):
    """涨停/跌停股票"""

    code: str
    name: str
    price: float
    change_pct: float  # 涨跌幅
    turnover: Optional[float] = None  # 换手率
    reason: Optional[str] = None  # 涨停/跌停原因
    limit_time: Optional[str] = None  # 首次封板时间


class LimitUpPoolProvider(BaseProvider[List[dict]]):
    """涨停池数据源

    参数:
        date: YYYYMMDD 格式，默认今日
    """

    def __init__(self, date: Optional[str] = None):
        self.date = date or ""

    async def _fetch(self) -> List[dict]:
        """从 akshare 获取涨停池数据"""

        def _do():
            df = ak.stock_zt_pool_em(date=self.date) if self.date else ak.stock_zt_pool_em()
            if df is None or df.empty:
                return []
            stocks = [
                LimitStock(
                    code=row.get("代码", ""),
                    name=row.get("名称", ""),
                    price=float(row.get("最新价") or 0),
                    change_pct=float(row.get("涨跌幅") or 0),
                    turnover=float(row.get("换手率") or 0) if row.get("换手率") else None,
                    reason=row.get("涨停原因"),
                    limit_time=row.get("首次封板时间"),
                )
                for _, row in df.iterrows()
            ]
            return [s.model_dump() for s in stocks]

        return await asyncio.to_thread(_do)

    @cached_json(namespace="limit_pool", key="limit_up_{date}", ttl=CacheTTL.NONE)
    async def get(self) -> List[dict]:
        """获取涨停池数据（不缓存）"""
        return await self._fetch()


class LimitDownPoolProvider(BaseProvider[List[dict]]):
    """跌停池数据源

    参数:
        date: YYYYMMDD 格式，默认今日（必须传，akshare 要求最近30交易日）
    """

    def __init__(self, date: Optional[str] = None):
        self.date = date or datetime.now().strftime("%Y%m%d")

    async def _fetch(self) -> List[dict]:
        """从 akshare 获取跌停池数据"""

        def _do():
            df = ak.stock_zt_pool_dtgc_em(date=self.date)
            if df is None or df.empty:
                return []
            stocks = [
                LimitStock(
                    code=row.get("代码", ""),
                    name=row.get("名称", ""),
                    price=float(row.get("最新价") or 0),
                    change_pct=float(row.get("涨跌幅") or 0),
                    turnover=float(row.get("换手率") or 0) if row.get("换手率") else None,
                    reason=row.get("跌停原因"),
                    limit_time=None,
                )
                for _, row in df.iterrows()
            ]
            return [s.model_dump() for s in stocks]

        return await asyncio.to_thread(_do)

    @cached_json(namespace="limit_pool", key="limit_down_{date}", ttl=CacheTTL.NONE)
    async def get(self) -> List[dict]:
        """获取跌停池数据（不缓存）"""
        return await self._fetch()
