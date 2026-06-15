from typing import Dict, List, Optional

from app.base.datasource_from import DatasourceFrom
from app.cache.file_cache import file_cache
from app.cache.policy import CachePolicy
from app.providers.index_data import (
    CORE_INDICES,
    STYLE_INDICES,
    get_core_indices_daily,
    get_index_daily_hist,
    get_index_spot_quotes,
    get_style_indices_daily,
)
from app.service.bean import tag_datasource
from app.service.fetch import with_cache
from app.service.indicators import enrich_index_indicators


async def get_core_index_analysis() -> Dict[str, List[dict]]:
    """三大指数日K + 均线/支撑压力/趋势判断。"""
    result: Dict[str, List[dict]] = {}
    for key, (code, name) in CORE_INDICES.items():
        cache_key = f"index_daily_{code}"

        async def _fetch(symbol=code, index_name=name):
            bars = await get_index_daily_hist(symbol, index_name)
            rows = tag_datasource(bars, DatasourceFrom.EAST_MONEY)
            return enrich_index_indicators(rows)

        result[key] = await with_cache(file_cache, cache_key, CachePolicy.DAILY, _fetch)
    return result


async def get_index_spot() -> List[dict]:
    async def _fetch():
        return tag_datasource(await get_index_spot_quotes(), DatasourceFrom.EAST_MONEY)

    return await with_cache(file_cache, "index_spot_em", CachePolicy.NONE, _fetch)


async def get_style_compare() -> Dict[str, dict]:
    """大小盘风格对比：沪深300 vs 中证1000/2000。"""
    async def _fetch():
        bars = await get_style_indices_daily()
        grouped: Dict[str, List[dict]] = {}
        for bar in bars:
            grouped.setdefault(bar.index_code or "", []).append(bar.model_dump())
        compare: Dict[str, dict] = {}
        for key, (code, name) in STYLE_INDICES.items():
            rows = grouped.get(code, [])
            latest = rows[-1] if rows else {}
            compare[key] = {
                "index_code": code,
                "index_name": name,
                "latest_close": latest.get("close"),
                "latest_change_pct": latest.get("change_pct"),
                "datasource": DatasourceFrom.EAST_MONEY.name,
            }
        if compare.get("hs300", {}).get("latest_change_pct") is not None and compare.get("zz1000"):
            compare["large_vs_small_spread"] = round(
                (compare["hs300"]["latest_change_pct"] or 0)
                - (compare["zz1000"]["latest_change_pct"] or 0),
                4,
            )
        return compare

    return await with_cache(file_cache, "style_compare", CachePolicy.DAILY, _fetch)
