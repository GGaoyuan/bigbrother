"""Share the agreed source priority and failure handling across stock queries."""

from app.core.exceptions import MarketDataError, ProviderUnavailable, StockNotFound, UnsupportedMarketData
from app.core.logger import observe_provider


def read_with_fallback(sources, label, symbol, reader, **parameters):
    failures = []
    for source in sources:
        try:
            with observe_provider(source.name, label, symbol=symbol, version=source.version, **parameters):
                return reader(source)
        except MarketDataError as exc:
            failures.append((source.name, exc))
    message = "；".join(f"{source}：{error}" for source, error in failures)
    if any(isinstance(exc, StockNotFound) for _, exc in failures):
        if all(isinstance(exc, (StockNotFound, UnsupportedMarketData)) for _, exc in failures):
            raise StockNotFound(f"未找到股票 {symbol}。{message}")
    if all(isinstance(exc, UnsupportedMarketData) for _, exc in failures):
        raise UnsupportedMarketData(message)
    raise ProviderUnavailable(message or "无可用行情数据源")
