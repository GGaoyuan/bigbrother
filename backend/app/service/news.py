from typing import Dict, List

from app.base.datasource_from import DatasourceFrom
from app.cache.file_cache import file_cache
from app.cache.policy import CachePolicy
from app.providers.news_macro import (
    get_macro_lpr,
    get_macro_market_operation,
    get_pywencai_hot_concepts,
    get_stock_news,
    get_us_index_quotes,
)
from app.service.bean import tag_datasource, sanitize_json
from app.service.fetch import with_cache


async def get_news_overview() -> Dict[str, object]:
    import asyncio

    async def _fetch():
        news, macro_op, lpr, us_indices = await asyncio.gather(
            get_stock_news("000001"),
            get_macro_market_operation(),
            get_macro_lpr(),
            get_us_index_quotes(),
        )
        hot_concepts: list = []
        return sanitize_json({
            "news": tag_datasource(news, DatasourceFrom.EAST_MONEY),
            "macro_operation": tag_datasource(macro_op, DatasourceFrom.EAST_MONEY),
            "lpr": tag_datasource(lpr, DatasourceFrom.EAST_MONEY),
            "us_indices": tag_datasource(us_indices, DatasourceFrom.SINA),
            "hot_concepts": hot_concepts,
        })

    return await with_cache(file_cache, "news_overview", CachePolicy.DAILY, _fetch)
