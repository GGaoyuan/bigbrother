from fastapi import HTTPException

from app.providers.baostock import BaoStockProvider
from app.providers.akshare import AKShareProvider


class MarketSentimentService:
    def __init__(self):
        self._providers = {
            "baostock": BaoStockProvider(),
            "akshare": AKShareProvider(),
        }
        self._fallback_order = ["baostock", "akshare"]

    async def get_market_stats(self, date: str) -> dict:
        for name in self._fallback_order:
            try:
                return await self._providers[name].get_market_stats(date)
            except Exception as e:
                print(f"[{name}] get_market_stats 失败: {e}")
                continue

        raise HTTPException(status_code=503, detail="所有数据源均不可用")
