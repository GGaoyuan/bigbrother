from typing import Dict, List, Optional

from app.base.datasource_from import DatasourceFrom
from app.cache.file_cache import file_cache
from app.cache.policy import CachePolicy
from app.providers.capital_data import (
    get_dragon_tiger_list,
    get_margin_sse,
    get_margin_szse,
    get_market_fund_flow,
    get_northbound_hist,
    get_northbound_summary,
)
from app.service.bean import tag_datasource
from app.service.fetch import with_cache


async def get_northbound_data() -> Dict[str, List[dict]]:
    import asyncio

    async def _fetch():
        summary, hist = await asyncio.gather(
            get_northbound_summary(),
            get_northbound_hist("北向资金"),
        )
        return {
            "summary": tag_datasource(summary, DatasourceFrom.EAST_MONEY),
            "history": tag_datasource(hist, DatasourceFrom.EAST_MONEY),
        }

    return await with_cache(file_cache, "northbound_data", CachePolicy.DAILY, _fetch)


async def get_margin_data() -> Dict[str, List[dict]]:
    import asyncio

    async def _fetch():
        sse, szse = await asyncio.gather(get_margin_sse(), get_margin_szse())
        return {
            "sse": tag_datasource(sse, DatasourceFrom.EAST_MONEY),
            "szse": tag_datasource(szse, DatasourceFrom.EAST_MONEY),
        }

    return await with_cache(file_cache, "margin_data", CachePolicy.DAILY, _fetch)


async def get_dragon_tiger(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    cache_key = f"dragon_tiger_{start_date or 'today'}_{end_date or 'today'}"

    async def _fetch():
        return tag_datasource(
            await get_dragon_tiger_list(start_date, end_date),
            DatasourceFrom.EAST_MONEY,
        )

    return await with_cache(file_cache, cache_key, CachePolicy.DAILY, _fetch)


async def get_market_capital_flow() -> List[dict]:
    async def _fetch():
        return tag_datasource(await get_market_fund_flow(), DatasourceFrom.EAST_MONEY)

    return await with_cache(file_cache, "market_capital_flow", CachePolicy.DAILY, _fetch)
