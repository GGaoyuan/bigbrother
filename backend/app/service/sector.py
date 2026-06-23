import asyncio
from typing import Dict, List, Optional

from app.cache import CacheTTL
from app.providers.board_data import (
    get_concept_board_quotes,
    get_industry_board_quotes,
    get_sector_fund_flow_rank,
    get_ths_concept_fund_flow,
    get_ths_industry_fund_flow,
)
from app.service.bean import tag_datasource
from app.service.fetch import with_json_cache


async def get_realtime_sectors(sector_type: int = 3) -> Dict[str, List[dict]]:
    """获取板块实时行情，不缓存。

    sector_type: 1=行业, 2=概念, 3=全部
    """
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
        result[key] = tag_datasource(items, "EAST_MONEY")
    return result


async def get_sector_fund_flow(
    indicator: str = "今日",
    sector_type: str = "行业资金流",
) -> List[dict]:
    """板块资金流排行，DAILY 缓存。

    indicator: 周期，如 "今日"。
    sector_type: 板块类型，如 "行业资金流"。
    """
    cache_key = f"sector_fund_flow_{indicator}_{sector_type}"

    async def _fetch():
        return tag_datasource(
            await get_sector_fund_flow_rank(indicator, sector_type),
            "EAST_MONEY",
        )

    return await with_json_cache(cache_key, CacheTTL.DAILY, _fetch)


async def get_ths_sector_fund_flow() -> Dict[str, List[dict]]:
    """同花顺行业/概念资金流。当前平台禁用，返回空数据。"""
    return {
        "ths_concept": [],
        "ths_industry": [],
        "error": "ths_api_disabled_on_current_platform",
    }
