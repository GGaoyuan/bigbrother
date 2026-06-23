from typing import Dict, List, Optional

from app.cache import CacheTTL
from app.providers.sw_industry_index import SwIndexBar, get_sw_index_hist
from app.service.fetch import with_json_cache
from app.service.industry import get_sw_industry

# 申万A指，代表全市场总市值走势
TOTAL_MARKET_SYMBOL = "801003"
TOTAL_MARKET_NAME = "申万A指"


def _bars_to_points(bars: List[SwIndexBar]) -> List[dict]:
    """转成前端图表点位 {time, value}，按日期升序，过滤空值。"""
    points: List[dict] = []
    for bar in bars:
        if bar.trade_date and bar.close is not None:
            points.append({"time": bar.trade_date, "value": bar.close})
    points.sort(key=lambda p: p["time"])
    return points


async def get_total_market_cap_trend() -> Dict[str, object]:
    """
    A股总市值走势（以申万A指日线代理）。
    缓存到 market_cap_total.csv，每日刷新。
    """
    cache_key = "market_cap_total"

    async def _fetch():
        bars = await get_sw_index_hist(TOTAL_MARKET_SYMBOL, period="day")
        return {
            "symbol": TOTAL_MARKET_SYMBOL,
            "name": TOTAL_MARKET_NAME,
            "points": _bars_to_points(bars),
        }

    return await with_json_cache(cache_key, CacheTTL.DAILY, _fetch)


async def get_industry_trend(symbol: str) -> Dict[str, object]:
    """
    单个申万行业指数走势。
    symbol: 申万指数代码（带或不带 .SI 后缀均可）。
    按行业代码分别缓存，每日刷新。
    """
    clean_symbol = symbol.replace(".SI", "").strip()
    cache_key = f"market_cap_industry_{clean_symbol}"

    async def _fetch():
        bars = await get_sw_index_hist(clean_symbol, period="day")
        return {
            "symbol": clean_symbol,
            "points": _bars_to_points(bars),
        }

    return await with_json_cache(cache_key, CacheTTL.DAILY, _fetch)


async def get_industry_tree() -> Dict[str, List[dict]]:
    """
    申万一/二/三级行业分类树（直接复用已有 service，带 WEEKLY 缓存）。
    """
    return await get_sw_industry()


async def get_total_volume_trend() -> Dict[str, object]:
    """
    A股总成交额走势（以申万A指成交额代理）。
    缓存到 market_volume_total.csv，每日刷新。
    """
    cache_key = "market_volume_total"

    async def _fetch():
        bars = await get_sw_index_hist(TOTAL_MARKET_SYMBOL, period="day")
        # 提取成交额（turnover）而非点位
        points: List[dict] = []
        for bar in bars:
            if bar.trade_date and bar.turnover is not None:
                points.append({"time": bar.trade_date, "value": bar.turnover})
        points.sort(key=lambda p: p["time"])
        return {
            "symbol": TOTAL_MARKET_SYMBOL,
            "name": "A股成交额",
            "points": points,
        }

    return await with_json_cache(cache_key, CacheTTL.DAILY, _fetch)


async def get_industry_volume(symbol: str) -> Dict[str, object]:
    """
    单个申万行业成交额走势。
    symbol: 申万指数代码（带或不带 .SI 后缀均可）。
    按行业代码分别缓存，每日刷新。
    """
    clean_symbol = symbol.replace(".SI", "").strip()
    cache_key = f"market_volume_industry_{clean_symbol}"

    async def _fetch():
        bars = await get_sw_index_hist(clean_symbol, period="day")
        points: List[dict] = []
        for bar in bars:
            if bar.trade_date and bar.turnover is not None:
                points.append({"time": bar.trade_date, "value": bar.turnover})
        points.sort(key=lambda p: p["time"])
        return {
            "symbol": clean_symbol,
            "points": points,
        }

    return await with_json_cache(cache_key, CacheTTL.DAILY, _fetch)
