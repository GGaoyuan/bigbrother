import asyncio
from typing import Dict, List

from app.cache.sw_industry_cache import sw_industry_cache
from app.providers.sw_industry_index import (
    get_sw_index_first_info,
    get_sw_index_second_info,
    get_sw_index_third_info,
)
from app.providers.sw_industry_component import get_sw_index_component

_CONCURRENCY = 25


async def get_sw_industry() -> Dict[str, List[dict]]:
    """
    获取申万一二三级行业数据及每个行业的成分股，带本地文件缓存（1天过期）。
    """
    cached = await sw_industry_cache.get()
    if cached is not None:
        return cached

    first_list, second_list, third_list = await asyncio.gather(
        _dump_list(get_sw_index_first_info()),
        _dump_list(get_sw_index_second_info()),
        _dump_list(get_sw_index_third_info()),
    )

    sem = asyncio.Semaphore(_CONCURRENCY)
    await _fill_stocks(third_list, sem)

    _aggregate_by_parent(second_list, third_list)
    _aggregate_by_parent(first_list, second_list)

    data = {"first": first_list, "second": second_list, "third": third_list}
    await sw_industry_cache.set(value=data)
    return data


async def _dump_list(coro) -> List[dict]:
    """await 一个返回 Pydantic 列表的协程并转成 dict 列表。"""
    items = await coro
    return [u.model_dump() for u in items]


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


def _aggregate_by_parent(parent_list: List[dict], child_list: List[dict]) -> None:
    """按上级行业名称把子级成分股聚合到父级，按 stock_code 去重。"""
    grouped: Dict[str, List[dict]] = {}
    for child in child_list:
        parent_name = child.get("sw_parent_industry")
        if not parent_name:
            continue
        grouped.setdefault(parent_name, []).extend(child.get("stocks") or [])

    for parent in parent_list:
        merged = grouped.get(parent["sw_industry_name"], [])
        seen = set()
        unique: List[dict] = []
        for s in merged:
            code = s.get("stock_code")
            if code in seen:
                continue
            seen.add(code)
            unique.append(s)
        parent["stocks"] = unique
