import json
import os
import time
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from .base import BaseCache

_CACHE_DIR = os.path.join(os.path.dirname(__file__), "data")
_SW_INDUSTRY_FILE = os.path.join(_CACHE_DIR, "sw_industry.json")
_SW_INDUSTRY_TTL = 86400  # 1天（秒）


class _DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


class SwIndustryCache(BaseCache):
    """申万行业数据文件缓存，过期时间 1 天。"""

    async def get(self, key: str = "sw_industry") -> Optional[Dict[str, List[dict]]]:
        if not os.path.exists(_SW_INDUSTRY_FILE):
            return None
        try:
            with open(_SW_INDUSTRY_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

        if time.time() - cache.get("cached_at", 0) > _SW_INDUSTRY_TTL:
            return None
        return cache.get("data")

    async def set(self, key: str = "sw_industry", value: Any = None, ttl: Optional[int] = None) -> None:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        cache = {
            "cached_at": time.time(),
            "data": value,
        }
        with open(_SW_INDUSTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, cls=_DateEncoder)


sw_industry_cache = SwIndustryCache()
