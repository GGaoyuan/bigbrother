import os
from datetime import datetime
from typing import Any, List, Optional

import pandas as pd

from .base import BaseCache
from .data_path import CACHE_DIR
from .freshness import is_cache_fresh
from .policy import CachePolicy


class FileCache(BaseCache):
    """
    通用 CSV 文件缓存。
    鲜度按自然日/周/月边界判断，由文件 mtime 决定缓存写入时间。
    """

    def __init__(self, cache_dir: os.PathLike = CACHE_DIR):
        self._cache_dir = os.fspath(cache_dir)

    def _path(self, key: str) -> str:
        safe_key = key.replace("/", "_").replace("\\", "_")
        return os.path.join(self._cache_dir, f"{safe_key}.csv")

    def is_fresh(self, key: str, policy: CachePolicy) -> bool:
        path = self._path(key)
        if not os.path.exists(path):
            return False
        cached_at = datetime.fromtimestamp(os.path.getmtime(path))
        return is_cache_fresh(cached_at, policy)

    async def get(self, key: str) -> Optional[List[dict]]:
        path = self._path(key)
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        return df.to_dict(orient="records")

    async def set(self, key: str, value: Any = None) -> None:
        path = self._path(key)
        os.makedirs(self._cache_dir, exist_ok=True)
        items = value or []
        pd.DataFrame(items).to_csv(path, index=False, encoding="utf-8-sig")


file_cache = FileCache()
