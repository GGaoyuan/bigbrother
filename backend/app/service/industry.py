import asyncio
import random
from typing import Awaitable, Callable, Dict, List

from app.cache.file_cache import file_cache
from app.cache.policy import CachePolicy
from app.providers.sw_industry_index import (
    get_sw_index_first_info,
    get_sw_index_second_info,
    get_sw_index_third_info,
)
from app.providers.sw_industry_component import get_sw_index_component
from app.service.fetch import with_cache

# 拉取成分股的并发数，太高会被申万限流
_COMPONENT_CONCURRENCY = 5

# 防封禁参数：每次请求前的随机延迟范围（秒），失败重试次数
_REQUEST_JITTER_RANGE = (0.3, 0.8)
_MAX_RETRIES = 3


def _make_dump_fetcher(
    fetcher: Callable[[], Awaitable[list]],
) -> Callable[[], Awaitable[List[dict]]]:
    async def _fetch() -> List[dict]:
        items = await fetcher()
        return [u.model_dump() for u in items]

    return _fetch


async def get_sw_industry() -> Dict[str, List[dict]]:
    """
    一次性获取申万一级、二级、三级行业列表。
    分别缓存到 sw_industry_first/second/third.csv。
    任一级别命中缓存就读 CSV，否则重新拉取并写入。串行拉取避免被申万限流。
    """
    levels = [
        ("first", "sw_industry_first", get_sw_index_first_info, CachePolicy.WEEKLY),
        ("second", "sw_industry_second", get_sw_index_second_info, CachePolicy.WEEKLY),
        ("third", "sw_industry_third", get_sw_index_third_info, CachePolicy.WEEKLY),
    ]

    result: Dict[str, List[dict]] = {}
    for name, key, fetcher, policy in levels:
        result[name] = await with_cache(
            file_cache, key, policy, _make_dump_fetcher(fetcher)
        )

    return result


async def _fetch_sw_stock_industry() -> List[dict]:
    """
    遍历所有三级行业拉取成分股，并补齐每只股票的一/二/三级行业归属。

    防封禁与效率平衡：
      - Semaphore 限制并发为 5
      - 每次请求前 0.3~0.8 秒随机抖动
      - 单个三级行业失败时按指数退避重试 3 次

    每条记录字段：
        stock_code, stock_name,
        sw_industry_l1_code, sw_industry_l1_name,
        sw_industry_l2_code, sw_industry_l2_name,
        sw_industry_l3_code, sw_industry_l3_name
    """
    industry_data = await get_sw_industry()
    first_list = industry_data.get("first", [])
    second_list = industry_data.get("second", [])
    third_list = industry_data.get("third", [])

    first_name_to_code = {
        item.get("sw_industry_name"): item.get("sw_industry_code")
        for item in first_list
        if item.get("sw_industry_name")
    }
    second_name_to_code = {
        item.get("sw_industry_name"): item.get("sw_industry_code")
        for item in second_list
        if item.get("sw_industry_name")
    }
    second_name_to_parent = {
        item.get("sw_industry_name"): item.get("sw_parent_industry")
        for item in second_list
        if item.get("sw_industry_name")
    }

    sem = asyncio.Semaphore(_COMPONENT_CONCURRENCY)

    async def _fetch_with_retry(industry: dict) -> List[dict]:
        l3_code = industry.get("sw_industry_code") or ""
        l3_name = industry.get("sw_industry_name") or ""
        l2_name = industry.get("sw_parent_industry") or ""

        l2_code = second_name_to_code.get(l2_name) or ""
        l1_name = second_name_to_parent.get(l2_name) or ""
        l1_code = first_name_to_code.get(l1_name) or ""

        symbol = l3_code.replace(".SI", "")
        if not symbol:
            return []

        async with sem:
            await asyncio.sleep(random.uniform(*_REQUEST_JITTER_RANGE))

            for attempt in range(_MAX_RETRIES):
                try:
                    stocks = await get_sw_index_component(symbol)
                    return [
                        {
                            "stock_code": s.stock_code or "",
                            "stock_name": s.stock_name or "",
                            "sw_industry_l1_code": l1_code,
                            "sw_industry_l1_name": l1_name,
                            "sw_industry_l2_code": l2_code,
                            "sw_industry_l2_name": l2_name,
                            "sw_industry_l3_code": l3_code,
                            "sw_industry_l3_name": l3_name,
                        }
                        for s in stocks
                    ]
                except Exception:
                    if attempt == _MAX_RETRIES - 1:
                        return []
                    await asyncio.sleep(2 ** attempt + random.random())
            return []

    grouped = await asyncio.gather(*[_fetch_with_retry(item) for item in third_list])

    seen: set = set()
    flat: List[dict] = []
    for rows in grouped:
        for row in rows:
            code = row.get("stock_code")
            if not code or code in seen:
                continue
            seen.add(code)
            flat.append(row)

    return flat


async def get_sw_stock_industry() -> List[dict]:
    """
    一次性获取所有三级申万行业对应的股票，并补齐每只股票的一/二/三级行业归属。
    缓存到 sw_stock_industry.csv，缓存有效期 1 个月。
    """
    return await with_cache(
        file_cache,
        "sw_stock_industry",
        CachePolicy.MONTHLY,
        _fetch_sw_stock_industry,
    )
