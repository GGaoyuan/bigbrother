from typing import Dict, List

from app.cache.file_cache import file_cache
from app.cache.policy import CachePolicy
from app.providers.tdx_data import get_tdx_daily_kline, get_tdx_quotes
from app.service.bean import tag_datasource
from app.service.fetch import with_cache


async def get_tdx_realtime_quotes(symbols: List[str]) -> List[dict]:
    """通达信实时行情快照，不缓存。

    symbols: 6 位证券代码列表。
    """
    items = await get_tdx_quotes(symbols)
    return tag_datasource(items, "TDX")


async def get_tdx_kline(symbol: str, offset: int = 60) -> Dict[str, object]:
    """通达信日线 K 线，按代码 DAILY 缓存。

    symbol: 6 位证券代码。
    offset: 返回最近多少根日线。
    """
    cache_key = f"tdx_kline_{symbol}_{offset}"

    async def _fetch():
        bars = await get_tdx_daily_kline(symbol, offset)
        rows = tag_datasource(bars, "TDX")
        return {"code": symbol, "bars": rows}

    return await with_cache(file_cache, cache_key, CachePolicy.DAILY, _fetch)
