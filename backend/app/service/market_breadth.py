from typing import Dict, List, Optional

from app.base.datasource_from import DatasourceFrom
from app.cache.file_cache import file_cache
from app.cache.policy import CachePolicy
from app.providers.market_breadth import (
    get_broken_limit_pool,
    get_individual_fund_flow_rank,
    get_limit_down_pool,
    get_limit_up_pool,
    get_market_turnover_snapshot,
    get_sse_summary,
    get_strong_pool,
    get_szse_summary,
)
from app.service.bean import tag_datasource
from app.service.fetch import with_cache


async def get_market_volume_summary() -> dict:
    async def _fetch():
        turnover, sse, szse = await _gather_volume_sources()
        return {
            "turnover_snapshot": {**turnover, "datasource": DatasourceFrom.EAST_MONEY.name},
            "sse_summary": tag_datasource(sse, DatasourceFrom.EAST_MONEY),
            "szse_summary": tag_datasource(szse, DatasourceFrom.EAST_MONEY),
        }

    return await with_cache(file_cache, "market_volume_summary", CachePolicy.DAILY, _fetch)


async def _gather_volume_sources():
    import asyncio

    turnover, sse, szse = await asyncio.gather(
        get_market_turnover_snapshot(),
        get_sse_summary(),
        get_szse_summary(),
    )
    return turnover, sse, szse


async def get_limit_pool_summary(date: Optional[str] = None) -> Dict[str, List[dict]]:
    import asyncio

    cache_key = f"limit_pool_{date or 'today'}"

    async def _fetch():
        limit_up, limit_down, broken, strong = await asyncio.gather(
            get_limit_up_pool(date),
            get_limit_down_pool(date),
            get_broken_limit_pool(date),
            get_strong_pool(date),
        )
        return {
            "limit_up": tag_datasource(limit_up, DatasourceFrom.EAST_MONEY),
            "limit_down": tag_datasource(limit_down, DatasourceFrom.EAST_MONEY),
            "broken_limit": tag_datasource(broken, DatasourceFrom.EAST_MONEY),
            "strong": tag_datasource(strong, DatasourceFrom.EAST_MONEY),
        }

    return await with_cache(file_cache, cache_key, CachePolicy.DAILY, _fetch)


async def get_fund_flow_rank(indicator: str = "今日") -> List[dict]:
    cache_key = f"fund_flow_rank_{indicator}"

    async def _fetch():
        return tag_datasource(
            await get_individual_fund_flow_rank(indicator),
            DatasourceFrom.EAST_MONEY,
        )

    return await with_cache(file_cache, cache_key, CachePolicy.DAILY, _fetch)
