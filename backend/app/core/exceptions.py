"""Market-data failures, independent of the HTTP transport."""


class MarketDataError(Exception):
    pass


class ProviderUnavailable(MarketDataError):
    pass


class UnsupportedMarketData(MarketDataError):
    pass


class StockNotFound(MarketDataError):
    pass
