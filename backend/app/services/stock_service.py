"""查询、校验和缓存股票资料。"""

from app.core.cache import ExpiringCache
from app.core.exceptions import ProviderUnavailable
from app.core.logger import log_provider, observe_provider
from app.core.symbols import stock_exchange
from app.models.model import StockLookup
from app.models.provider import MarketDataProvider


class StockInfoService:
    def __init__(self, source: MarketDataProvider):
        self.source = source
        self.lookup_cache = ExpiringCache(256)

    def get_stock(self, symbol: str) -> StockLookup:
        exchange = stock_exchange(symbol)

        source = self.source
        key = (source.name, source.version, symbol)
        with observe_provider(source.name, "stock", symbol=symbol, version=source.version):
            info = self.lookup_cache.get(key)
            if info is None:
                info = source.get_stock_info(symbol)
                if info.symbol != symbol or info.exchange != exchange or not info.name.strip():
                    raise ProviderUnavailable("股票代码、交易所或名称校验失败")
                self.lookup_cache.put(key, info, 3600)
            else:
                log_provider("cache_hit", source.name, "stock", symbol=symbol)
            return StockLookup(
                info, source.name, source.version, (source.name,), (source.name,),
            )
