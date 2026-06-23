"""统一的缓存模块入口。

```python
from app.cache import json_cache, csv_cache, CacheTTL

await json_cache.set("tdx_kline_600000", payload, ttl=CacheTTL.DAILY)
data = await json_cache.get("tdx_kline_600000")

await csv_cache.set("sw_industry_first", rows, ttl=CacheTTL.WEEKLY)
rows = await csv_cache.get("sw_industry_first")
```
"""

from app.cache.base import Cache, CacheMeta
from app.cache.csv_cache import CsvCache, csv_cache
from app.cache.json_cache import JsonCache, json_cache
from app.cache.ttl import CacheTTL

__all__ = [
    "Cache",
    "CacheMeta",
    "CacheTTL",
    "CsvCache",
    "JsonCache",
    "csv_cache",
    "json_cache",
]
