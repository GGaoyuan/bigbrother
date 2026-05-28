import asyncio
from typing import Dict, List

from app.cache.sw_industry_cache import sw_industry_cache
from app.providers.ak_provider import (
    get_sw_index_first_info,
    get_sw_index_second_info,
    get_sw_index_third_info,
    get_sw_index_component,
)

_CONCURRENCY = 5


async def get_sw_industry() -> Dict[str, List[dict]]:
    """
    获取申万一二三级行业数据及每个行业的成分股，带本地文件缓存（1天过期）。

    Returns:
        {
            "first": [{"sw_industry_code", "sw_industry_name", ..., "stocks": [...]}],
            "second": [...],
            "third": [...]
        }
    """
    cached = await sw_industry_cache.get()
    if cached is not None:
        return cached

    first_list = [u.model_dump() for u in await get_sw_index_first_info()]
    second_list = [u.model_dump() for u in await get_sw_index_second_info()]
    third_list = [u.model_dump() for u in await get_sw_index_third_info()]

    sem = asyncio.Semaphore(_CONCURRENCY)
    await _fill_stocks(first_list, sem)
    await _fill_stocks(second_list, sem)
    await _fill_stocks(third_list, sem)

    data = {"first": first_list, "second": second_list, "third": third_list}
    await sw_industry_cache.set(value=data)
    return data


async def _fill_stocks(industry_list: List[dict], sem: asyncio.Semaphore) -> None:
    """为行业列表中的每个行业并发获取成分股。"""

    async def _fetch_one(item: dict):
        code = item["sw_industry_code"].replace(".SI", "")
        async with sem:
            try:
                stocks = await get_sw_index_component(code)
                item["stocks"] = [s.model_dump() for s in stocks]
            except Exception:
                item["stocks"] = []

    await asyncio.gather(*[_fetch_one(item) for item in industry_list])
