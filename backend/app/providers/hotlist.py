"""热榜数据 provider — 涨跌停池、个股排行（完全符合 BaseProvider 规范）。

数据源优先级（按 memory 记录）：
1. mootdx（通达信协议，但无排行接口）
2. efinance（东财，部分接口不稳定）
3. akshare（东财/同花顺，网络间歇性中断）

实际可用：
- ✓ akshare 涨跌停池（ak.stock_zt_pool_em 系列）
- ✓ akshare 个股资金流排行（偶尔中断，需重试）
"""

import asyncio
import time
from datetime import datetime
from typing import List, Optional

import akshare as ak
from pydantic import BaseModel

from app.cache import CacheTTL
from app.providers.base_provider import BaseProvider
from app.providers.cache_decorator import cached_json


# ========== Models ==========
class LimitStock(BaseModel):
    """涨停/跌停股票"""

    code: str
    name: str
    price: float
    change_pct: float  # 涨跌幅
    turnover: Optional[float] = None  # 换手率
    reason: Optional[str] = None  # 涨停原因
    limit_time: Optional[str] = None  # 涨停时间


class FundFlowRankItem(BaseModel):
    """个股资金流排行条目"""

    code: str
    name: str
    price: float
    change_pct: float
    main_net_inflow: float  # 主力净流入（元）
    main_net_inflow_pct: float  # 主力净流入占比


# ========== Helper ==========
def _retry(fn, tries: int = 3, gap_s: float = 1.5):
    """重试包装，扛东财间歇性中断"""
    last_err = None
    for _ in range(tries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(gap_s)
    raise last_err


# ========== 涨停池 Provider ==========
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

    @cached_json(key="limit_up_pool_{date}", ttl=CacheTTL.HOURLY)
    async def get(self) -> List[dict]:
        """获取涨停池数据（带 1 小时缓存）"""
        return await self._fetch()


# ========== 跌停池 Provider ==========
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

    @cached_json(key="limit_down_pool_{date}", ttl=CacheTTL.HOURLY)
    async def get(self) -> List[dict]:
        """获取跌停池数据（带 1 小时缓存）"""
        return await self._fetch()


# ========== 个股资金流排行 Provider ==========
class FundFlowRankProvider(BaseProvider[List[dict]]):
    """个股主力资金流排行数据源

    参数:
        indicator: 今日/3日/5日/10日
        limit: 返回数量上限
    """

    def __init__(self, indicator: str = "今日", limit: int = 100):
        self.indicator = indicator
        self.limit = limit

    async def _fetch(self) -> List[dict]:
        """从 akshare 获取资金流排行（带重试）"""

        def _do():
            df = _retry(lambda: ak.stock_individual_fund_flow_rank(indicator=self.indicator))
            if df is None or df.empty:
                return []
            items = []
            for _, row in df.head(self.limit).iterrows():
                items.append(
                    FundFlowRankItem(
                        code=row.get("代码", ""),
                        name=row.get("名称", ""),
                        price=float(row.get("最新价") or 0),
                        change_pct=float(row.get("涨跌幅") or 0),
                        main_net_inflow=float(row.get("主力净流入-净额") or 0),
                        main_net_inflow_pct=float(row.get("主力净流入-净占比") or 0),
                    )
                )
            return [x.model_dump() for x in items]

        return await asyncio.to_thread(_do)

    @cached_json(key="fund_flow_rank_{indicator}_{limit}", ttl=CacheTTL.HOURLY)
    async def get(self) -> List[dict]:
        """获取资金流排行（带 1 小时缓存）"""
        return await self._fetch()
