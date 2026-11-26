"""Stock metadata lookup, validation and source selection."""

from app.core.cache import ExpiringCache
from app.core.exceptions import ProviderUnavailable
from app.core.logger import log_provider
from app.core.symbols import stock_exchange
from app.models.stock import StockLookup
from app.models.contracts import StockDataSource

from ._fallback import read_with_fallback


class StockInfoService:
    def __init__(self, sources: tuple[StockDataSource, ...]):
        self.sources = sources
        self.lookup_cache = ExpiringCache(256)

    def get_stock(self, symbol: str) -> StockLookup:
        exchange = stock_exchange(symbol)

        def read(source: StockDataSource) -> StockLookup:
            key = (source.name, source.version, symbol)
            info = self.lookup_cache.get(key)
            if info is None:
                info = source.get_stock_info(symbol)
                if info.symbol != symbol or info.exchange != exchange or not info.name.strip():
                    raise ProviderUnavailable("股票代码、交易所或名称校验失败")
                self.lookup_cache.put(key, info, 3600)
            else:
                log_provider("cache_hit", source.name, "stock", symbol=symbol)
            available = [
                item.name for item in self.sources
                if self.lookup_cache.get((item.name, item.version, symbol)) is not None
            ]
            return StockLookup(
                info, source.name, source.version, tuple(available),
                tuple(item.name for item in self.sources),
            )

        return read_with_fallback(self.sources, "stock", symbol, read)
