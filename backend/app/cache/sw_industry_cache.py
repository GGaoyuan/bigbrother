import os
import time
from typing import Any, List, Optional

import pandas as pd

from .base import BaseCache

# 缓存目录
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "data")

# 申万行业相关的缓存键 -> CSV 文件名
_KEY_TO_FILE = {
    "sw_industry_first": "sw_industry_first.csv",        # 一级行业
    "sw_industry_second": "sw_industry_second.csv",      # 二级行业
    "sw_industry_third": "sw_industry_third.csv",        # 三级行业
    "sw_stock_industry": "sw_stock_industry.csv",        # 三级行业对应的全市场股票
}

# 默认缓存有效期 3 天（秒）
_DEFAULT_TTL = 3 * 86400


class SwIndustryCache(BaseCache):
    """
    申万行业数据 CSV 文件缓存。
    每个 key 对应一个 CSV 文件，过期时间默认 3 天，由文件 mtime 判断鲜度。
    """

    def _path(self, key: str) -> str:
        """根据 key 取对应 CSV 文件的绝对路径"""
        if key not in _KEY_TO_FILE:
            raise ValueError(f"未注册的缓存 key: {key}")
        return os.path.join(_CACHE_DIR, _KEY_TO_FILE[key])

    def is_fresh(self, key: str, ttl: Optional[int] = None) -> bool:
        """判断指定 key 的缓存是否存在且未过期"""
        path = self._path(key)
        if not os.path.exists(path):
            return False
        return (time.time() - os.path.getmtime(path)) <= (ttl or _DEFAULT_TTL)

    async def get(self, key: str) -> Optional[List[dict]]:
        """读取 CSV 缓存（不做鲜度判断，由调用方先用 is_fresh 检查）"""
        path = self._path(key)
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        return df.to_dict(orient="records")

    async def set(self, key: str, value: Any = None, ttl: Optional[int] = None) -> None:
        """将 dict 列表写入对应 CSV 文件，ttl 仅用于文档语义（实际由 mtime 判断）"""
        path = self._path(key)
        os.makedirs(_CACHE_DIR, exist_ok=True)
        items = value or []
        pd.DataFrame(items).to_csv(path, index=False, encoding="utf-8-sig")


sw_industry_cache = SwIndustryCache()
