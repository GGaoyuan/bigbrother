from fastapi import HTTPException

from app.providers.baostock import BaoStockProvider
from app.providers.akshare import AKShareProvider
from app.core.config import settings


class MarketSentimentService:
    def __init__(self):
        self._providers = {
            "baostock": BaoStockProvider(),
            "akshare": AKShareProvider(),
        }
        # 从配置文件读取默认数据源
        self._default_provider = settings.datasource

    async def get_market_stats(self, date: str) -> dict:
        try:
            return await self._providers[self._default_provider].get_market_sentiment(date)
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"{self._default_provider} 数据源不可用: {e}"
            )
