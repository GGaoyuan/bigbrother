import csv
import json
import os
from datetime import datetime, timedelta
from typing import Any, List, Optional

from .base import BaseCache
from .data_path import CACHE_DIR
from .freshness import is_cache_fresh
from .policy import CachePolicy


class FileCache(BaseCache):
    """
    通用文件缓存。
    - list[dict] 存为 CSV
    - dict / 其他 JSON 可序列化结构存为 JSON
    鲜度按自然日/周/月边界判断，由文件 mtime 决定缓存写入时间。
    """

    def __init__(self, cache_dir: os.PathLike = CACHE_DIR):
        self._cache_dir = os.fspath(cache_dir)

    def _safe_key(self, key: str) -> str:
        return key.replace("/", "_").replace("\\", "_")

    def _csv_path(self, key: str) -> str:
        return os.path.join(self._cache_dir, f"{self._safe_key(key)}.csv")

    def _json_path(self, key: str) -> str:
        return os.path.join(self._cache_dir, f"{self._safe_key(key)}.json")

    def _existing_path(self, key: str) -> Optional[str]:
        json_path = self._json_path(key)
        if os.path.exists(json_path):
            return json_path
        csv_path = self._csv_path(key)
        if os.path.exists(csv_path):
            return csv_path
        return None

    def is_fresh(self, key: str, policy: CachePolicy) -> bool:
        path = self._existing_path(key)
        if not path:
            return False
        cached_at = datetime.fromtimestamp(os.path.getmtime(path))
        return is_cache_fresh(cached_at, policy)

    async def get(self, key: str) -> Optional[Any]:
        json_path = self._json_path(key)
        if os.path.exists(json_path):
            with open(json_path, encoding="utf-8") as f:
                return json.load(f)

        csv_path = self._csv_path(key)
        if not os.path.exists(csv_path):
            return None
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    async def set(self, key: str, value: Any = None) -> None:
        os.makedirs(self._cache_dir, exist_ok=True)

        if isinstance(value, list):
            csv_path = self._csv_path(key)
            json_path = self._json_path(key)
            if os.path.exists(json_path):
                os.remove(json_path)
            if not value:
                open(csv_path, "w", encoding="utf-8-sig").close()
                return
            fieldnames: List[str] = list(value[0].keys())
            for item in value[1:]:
                for key_name in item:
                    if key_name not in fieldnames:
                        fieldnames.append(key_name)
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(value)
            return

        json_path = self._json_path(key)
        csv_path = self._csv_path(key)
        if os.path.exists(csv_path):
            os.remove(csv_path)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, default=str)


file_cache = FileCache()
