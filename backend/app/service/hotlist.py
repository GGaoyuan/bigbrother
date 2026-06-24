"""热榜 service — 涨跌停池、资金流排行（完全符合 BaseService 规范）。

使用示例：
    service = LimitPoolsService()
    result = await service.execute()
    if result.success:
        pools = result.data
"""

import asyncio
from typing import Dict, List

from app.providers.hotlist import FundFlowRankProvider
from app.providers.limit_pool import LimitDownPoolProvider, LimitUpPoolProvider
from app.service.base_service import BaseService


class LimitPoolsService(BaseService[Dict[str, List[dict]]]):
    """涨停池 + 跌停池 Service

    返回: {"limit_up": [...], "limit_down": [...]}
    缓存: provider 层已处理（1小时）
    """

    async def _execute(self) -> Dict[str, List[dict]]:
        # 并发调用两个 provider
        limit_up_task = LimitUpPoolProvider().get()
        limit_down_task = LimitDownPoolProvider().get()
        limit_up, limit_down = await asyncio.gather(limit_up_task, limit_down_task)
        return {"limit_up": limit_up, "limit_down": limit_down}


class FundFlowRankingService(BaseService[Dict[str, List[dict]]]):
    """个股资金流排行 Service

    返回: {"inflow": [...], "outflow": [...]}
    缓存: provider 层已处理（1小时）
    降级: 东财接口不稳定，失败时通过 Result.fail 返回错误
    """

    def __init__(self, indicator: str = "今日", limit: int = 100):
        self.indicator = indicator
        self.limit = limit

    async def _execute(self) -> Dict[str, List[dict]]:
        # 调用 provider（取 2 倍数量，后续分流入/流出）
        provider = FundFlowRankProvider(self.indicator, self.limit * 2)
        all_items = await provider.get()

        # 按主力净流入排序，正值=流入、负值=流出
        all_items.sort(key=lambda x: x["main_net_inflow"], reverse=True)
        inflow = [x for x in all_items if x["main_net_inflow"] > 0][: self.limit]
        outflow = [x for x in all_items if x["main_net_inflow"] < 0][: self.limit]
        return {"inflow": inflow, "outflow": outflow}
