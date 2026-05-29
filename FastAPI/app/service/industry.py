import asyncio
import os
import time
from typing import Dict, List

import pandas as pd

from app.providers.sw_industry_index import (
    get_sw_index_first_info,
    get_sw_index_second_info,
    get_sw_index_third_info,
)
from app.providers.sw_industry_component import get_sw_index_component

# CSV 缓存目录与文件路径
_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "data")
_FIRST_CSV = os.path.join(_CACHE_DIR, "sw_industry_first.csv")
_SECOND_CSV = os.path.join(_CACHE_DIR, "sw_industry_second.csv")
_THIRD_CSV = os.path.join(_CACHE_DIR, "sw_industry_third.csv")
_STOCK_INDUSTRY_CSV = os.path.join(_CACHE_DIR, "sw_stock_industry.csv")

# 缓存有效期 1 天
_TTL_SECONDS = 86400

# 拉取成分股的并发数，太高会被申万限流
_COMPONENT_CONCURRENCY = 5


def _is_fresh(path: str) -> bool:
    """判断文件是否存在且未过期"""
    if not os.path.exists(path):
        return False
    return (time.time() - os.path.getmtime(path)) <= _TTL_SECONDS


def _read_csv(path: str) -> List[dict]:
    """读取 CSV 并转为 dict 列表"""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return df.to_dict(orient="records")


def _write_csv(path: str, items: List[dict]) -> None:
    """将 dict 列表写入 CSV"""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    pd.DataFrame(items).to_csv(path, index=False, encoding="utf-8-sig")


async def get_sw_industry() -> Dict[str, List[dict]]:
    """
    获取申万一级、二级、三级行业列表。
    分别缓存到 sw_industry_first/second/third.csv，缓存有效期 1 天。
    缓存命中则读 CSV，否则重新拉取并写入。
    """
    levels = [
        ("first", _FIRST_CSV, get_sw_index_first_info),
        ("second", _SECOND_CSV, get_sw_index_second_info),
        ("third", _THIRD_CSV, get_sw_index_third_info),
    ]

    async def _load_one(path: str, fetcher) -> List[dict]:
        if _is_fresh(path):
            return _read_csv(path)
        items = [u.model_dump() for u in await fetcher()]
        _write_csv(path, items)
        return items

    # 串行执行，避免并发请求被申万限流（返回空页面导致解析失败）
    result: Dict[str, List[dict]] = {}
    for name, path, fetcher in levels:
        result[name] = await _load_one(path, fetcher)

    return result


async def get_sw_stock_industry() -> List[dict]:
    """
    获取所有股票的三级申万行业归属。
    缓存到 sw_stock_industry.csv，缓存有效期 1 天。
    缓存命中则直接读 CSV，否则遍历所有三级行业拉取成分股并反向映射后写入。

    每条记录字段：
        stock_code, stock_name, sw_industry_code, sw_industry_name,
        sw_parent_industry, sw_weight, sw_inclusion_date
    """
    if _is_fresh(_STOCK_INDUSTRY_CSV):
        return _read_csv(_STOCK_INDUSTRY_CSV)

    # 拿到所有三级行业（会复用三级行业 CSV 缓存）
    industry_data = await get_sw_industry()
    third_list = industry_data.get("third", [])

    sem = asyncio.Semaphore(_COMPONENT_CONCURRENCY)

    async def _fetch_one(industry: dict) -> List[dict]:
        # 行业代码去掉 .SI 后缀
        code = (industry.get("sw_industry_code") or "").replace(".SI", "")
        if not code:
            return []
        async with sem:
            try:
                stocks = await get_sw_index_component(code)
            except Exception:
                return []
        return [
            {
                "stock_code": s.stock_code,
                "stock_name": s.stock_name,
                "sw_industry_code": industry.get("sw_industry_code"),
                "sw_industry_name": industry.get("sw_industry_name"),
                "sw_parent_industry": industry.get("sw_parent_industry"),
                "sw_weight": s.sw_weight,
                "sw_inclusion_date": s.sw_inclusion_date,
            }
            for s in stocks
        ]

    grouped = await asyncio.gather(*[_fetch_one(item) for item in third_list])

    # 扁平化并按 stock_code 去重，避免一只股票出现在多个三级行业里造成重复行
    seen = set()
    flat: List[dict] = []
    for rows in grouped:
        for row in rows:
            code = row.get("stock_code")
            if not code or code in seen:
                continue
            seen.add(code)
            flat.append(row)

    _write_csv(_STOCK_INDUSTRY_CSV, flat)
    return flat

