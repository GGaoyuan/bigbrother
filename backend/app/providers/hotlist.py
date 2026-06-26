"""个股资金流排行 provider（完全符合 BaseProvider 规范）
# DEPRECATED: 此文件使用 akshare/efinance/adata 数据源，已禁用，需要迁移到 easy_tdx/mootdx


数据源：akshare 东财个股资金流排行接口（不稳定，需重试）
不缓存：ttl=CacheTTL.NONE（需要缓存时改 ttl 即可）
"""

import asyncio
import time
from typing import List

import akshare as ak
from pydantic import BaseModel

from app.cache import CacheTTL
from app.providers.base_provider import BaseProvider
from app.providers.cache_decorator import cached_json


class FundFlowRankItem(BaseModel):
    """个股资金流排行条目"""

    code: str
    name: str
    price: float
    change_pct: float
    main_net_inflow: float  # 主力净流入（元）
    main_net_inflow_pct: float  # 主力净流入占比


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

    @cached_json(
        namespace="fund_flow_rank",
        key="rank_{indicator}_{limit}",
        ttl=CacheTTL.NONE,
    )
    async def get(self) -> List[dict]:
        """获取资金流排行（不缓存）"""
        return await self._fetch()
