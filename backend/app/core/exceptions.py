"""与 HTTP 传输层解耦的行情异常。"""


class MarketDataError(Exception):
    pass


class ProviderUnavailable(MarketDataError):
    pass


class UnsupportedMarketData(MarketDataError):
    pass


class StockNotFound(MarketDataError):
    pass
