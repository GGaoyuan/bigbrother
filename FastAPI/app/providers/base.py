from abc import ABC, abstractmethod
from app.bean import DailyBarBean, RealtimeQuoteBean, MarketSentimentBean


class StockProvider(ABC):
    @abstractmethod
    async def get_daily(self, code: str, start: str, end: str) -> list[DailyBarBean]: ...

    @abstractmethod
    async def get_realtime(self, code: str) -> RealtimeQuoteBean: ...

    @abstractmethod
    async def get_market_sentiment(self, date: str) -> MarketSentimentBean: ...
