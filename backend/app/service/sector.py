from typing import Dict, List, Optional

from app.base.datasource_from import DatasourceFrom
from app.cache.file_cache import file_cache
from app.cache.policy import CachePolicy
from app.providers.board_data import (
    get_concept_board_quotes,
    get_industry_board_quotes,
    get_sector_fund_flow_rank,
    get_ths_concept_fund_flow,
    get_ths_industry_fund_flow,
)
from app.service.bean import tag_datasource
from app.service.fetch import with_cache


async def get_realtime_sectors(sector_type: int = 3) -> Dict[str, List[dict]]:
    """
    获取板块实时行情。
    sector_type: 1=行业, 2=概念, 3=全部
    """
    cache_key = f"realtime_sectors_{sector_type}"

    async def _fetch():
        import asyncio

        result: Dict[str, List[dict]] = {}
        tasks = []
        keys = []
        if sector_type in (2, 3):
            keys.append("concept")
            tasks.append(get_concept_board_quotes())
        if sector_type in (1, 3):
            keys.append("industry")
            tasks.append(get_industry_board_quotes())
        grouped = await asyncio.gather(*tasks)
        for key, items in zip(keys, grouped):
            source = DatasourceFrom.EAST_MONEY
            result[key] = tag_datasource(items, source)
        return result

    return await with_cache(file_cache, cache_key, CachePolicy.NONE, _fetch)


async def get_sector_fund_flow(
    indicator: str = "今日",
    sector_type: str = "行业资金流",
) -> List[dict]:
    cache_key = f"sector_fund_flow_{indicator}_{sector_type}"

    async def _fetch():
        return tag_datasource(
            await get_sector_fund_flow_rank(indicator, sector_type),
            DatasourceFrom.EAST_MONEY,
        )

    return await with_cache(file_cache, cache_key, CachePolicy.DAILY, _fetch)


async def get_ths_sector_fund_flow() -> Dict[str, List[dict]]:
    """
    同花顺行业/概念资金流。
    注意：akshare 同花顺接口依赖 py_mini_racer，在部分 macOS 环境会崩溃，默认返回空数据。
    """
    return {
        "ths_concept": [],
        "ths_industry": [],
        "error": "ths_api_disabled_on_current_platform",
    }
