from typing import Optional
from fastapi import HTTPException

from app.providers.baostock import BaoStockProvider
from app.providers.akshare import AKShareProvider
from app.providers.tushare import TuShareProvider
from app.cache.noop import get_cache


class StockService:
    def __init__(self):
        self._providers = {
            "baostock": BaoStockProvider(),
            "akshare": AKShareProvider(),
            "tushare": TuShareProvider(),
        }
        self._fallback_order = ["baostock", "akshare", "tushare"]
        self._cache = get_cache()

    async def get_daily(
        self, code: str, start: str, end: str, provider: Optional[str] = None
    ) -> list:
        cache_key = f"daily:{code}:{start}:{end}:{provider or 'auto'}"

        if cached := await self._cache.get(cache_key):
            return cached

        if provider:
            try:
                data = await self._providers[provider].get_daily(code, start, end)
                await self._cache.set(cache_key, data)
                return data
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"{provider} 数据源不可用: {e}")

        for name in self._fallback_order:
            try:
                data = await self._providers[name].get_daily(code, start, end)
                await self._cache.set(cache_key, data)
                return data
            except Exception:
                continue

        raise HTTPException(status_code=503, detail="所有数据源均不可用")

    async def get_realtime(self, code: str, provider: Optional[str] = None) -> dict:
        cache_key = f"realtime:{code}:{provider or 'auto'}"

        if cached := await self._cache.get(cache_key):
            return cached

        if provider:
            try:
                data = await self._providers[provider].get_realtime(code)
                await self._cache.set(cache_key, data, ttl=10)
                return data
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"{provider} 数据源不可用: {e}")

        for name in self._fallback_order:
            try:
                data = await self._providers[name].get_realtime(code)
                await self._cache.set(cache_key, data, ttl=10)
                return data
            except Exception:
                continue

        raise HTTPException(status_code=503, detail="所有数据源均不可用")
