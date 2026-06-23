from typing import Dict, List

from app.cache import CacheTTL, json_cache
from app.providers.sector_intraday import (
    SectorIntraday,
    SectorSnapshot,
    get_concept_boards_snapshot,
    get_sector_intraday,
)


async def get_sector_intraday_ranking(top_n: int = 12, bottom_n: int = 12) -> Dict[str, List[dict]]:
    """板块日内资金流向排行榜 + top/bottom 走势。

    返回：
      {
        "ranking": [ 所有板块按最新净流入降序，格式 {code, name, net_inflow} ],
        "inflow_trends": [ top_n 流入板块的逐分钟曲线 ],
        "outflow_trends": [ bottom_n 流出板块的逐分钟曲线 ]
      }

    盘中用 1 小时缓存（实时性 vs 节省请求），盘后当天数据按日缓存。
    """
    cache_key = "sector_intraday_ranking"

    async def _fetch():
        # 1. 取所有概念板块快照，按净流入降序
        snapshots = await get_concept_boards_snapshot()
        snapshots.sort(key=lambda s: s.net_inflow, reverse=True)

        # 2. top N 流入 + bottom N 流出各取逐分钟曲线
        top = snapshots[:top_n]
        bottom = snapshots[-bottom_n:] if len(snapshots) >= bottom_n else []

        # 并发取曲线
        import asyncio
        tasks_in = [get_sector_intraday(s.code) for s in top]
        tasks_out = [get_sector_intraday(s.code) for s in bottom]
        inflow_trends = await asyncio.gather(*tasks_in)
        outflow_trends = await asyncio.gather(*tasks_out)

        return {
            "ranking": [s.model_dump() for s in snapshots],
            "inflow_trends": [t.model_dump() for t in inflow_trends],
            "outflow_trends": [t.model_dump() for t in outflow_trends],
        }

    # 盘中 1 小时缓存；若要区分盘中/盘后，可加个时间判断
    cached = await json_cache.get(cache_key)
    if cached is not None:
        return cached
    value = await _fetch()
    await json_cache.set(cache_key, value, ttl=CacheTTL.HOURLY)
    return value
