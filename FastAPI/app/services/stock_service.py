from typing import Optional
from fastapi import HTTPException

from app.providers.baostock import BaoStockProvider
from app.providers.akshare import AKShareProvider
from app.cache.noop import get_cache
from app.core.config import settings


class StockService:
    def __init__(self):
        self._providers = {
            "baostock": BaoStockProvider(),
            "akshare": AKShareProvider(),
        }
        # 从配置文件读取默认数据源
        self._default_provider = settings.datasource
        self._cache = get_cache()

    async def get_daily(
        self, code: str, start: str, end: str, provider: Optional[str] = None
    ) -> list:
        # 如果没有指定 provider，使用配置文件中的默认数据源
        provider = provider or self._default_provider
        cache_key = f"daily:{code}:{start}:{end}:{provider}"

        if cached := await self._cache.get(cache_key):
            return cached

        try:
            data = await self._providers[provider].get_daily(code, start, end)
            await self._cache.set(cache_key, data)
            return data
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"{provider} 数据源不可用: {e}")

    async def get_realtime(self, code: str, provider: Optional[str] = None) -> dict:
        # 如果没有指定 provider，使用配置文件中的默认数据源
        provider = provider or self._default_provider
        cache_key = f"realtime:{code}:{provider}"

        if cached := await self._cache.get(cache_key):
            return cached

        try:
            data = await self._providers[provider].get_realtime(code)
            await self._cache.set(cache_key, data, ttl=10)
            return data
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"{provider} 数据源不可用: {e}")
