"""校验、缓存并生成图表 K 线。"""

from math import isfinite

from app.core.cache import ExpiringCache
from app.core.exceptions import ProviderUnavailable, UnsupportedMarketData
from app.core.logger import log_provider, observe_provider
from app.core.symbols import stock_exchange
from app.models.kline.model import (
    Candle, ChartHistory, ChartInterval, Interval, KlineHistory,
)
from app.models.kline.provider import KlineProvider


def has_valid_ohlcv(bar: Candle) -> bool:
    return (
        all(isfinite(price) for price in (bar.open, bar.high, bar.low, bar.close))
        and 0 < bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high
        and type(bar.volume) is int and bar.volume >= 0
        and (bar.amount is None or (isfinite(bar.amount) and bar.amount >= 0))
    )


class KlineService:
    def __init__(self, source: KlineProvider):
        self.source = source
        self.history_cache = ExpiringCache(256)

    @staticmethod
    def _validate_bars(
        bars: tuple[Candle, ...], start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]:
        by_time = {}
        for bar in bars:
            if not has_valid_ohlcv(bar) or not 0 <= bar.timestamp < bar.end_timestamp or bar.adjustment != "qfq":
                raise ProviderUnavailable("K 线包含非法时间、价格、成交量或复权口径")
            if ((start is not None and bar.end_timestamp <= start) or
                    (end is not None and bar.timestamp >= end)):
                continue
            existing = by_time.get(bar.timestamp)
            if existing is not None and existing != bar:
                raise ProviderUnavailable("K 线包含冲突的重复时间")
            by_time[bar.timestamp] = bar
        ordered = tuple(by_time[key] for key in sorted(by_time)[-limit:])
        if not ordered:
            raise ProviderUnavailable("所请求区间无 K 线数据")
        if any(first.end_timestamp > second.timestamp for first, second in zip(ordered, ordered[1:])):
            raise ProviderUnavailable("K 线包含重叠时间区间")
        return ordered

    def get_history(
        self, symbol: str, interval: Interval,
        start: int | None, end: int | None, limit: int,
    ) -> KlineHistory:
        stock_exchange(symbol)

        source = self.source
        adjustment_version = source.adjustment_version
        with observe_provider(
            source.name, "klines", symbol=symbol, version=source.version,
            interval=interval, adjust="qfq", start=start, end=end, limit=limit,
        ):
            key = (source.name, source.version, adjustment_version, symbol, interval, start, end, limit)
            bars = self.history_cache.get(key)
            if bars is None:
                bars = self._validate_bars(
                    source.get_klines(symbol, interval, "qfq", start, end, limit),
                    start, end, limit,
                )
                self.history_cache.put(key, bars, 30)
            else:
                log_provider("cache_hit", source.name, "klines", symbol=symbol, interval=interval)
            return KlineHistory(bars, source.name, source.version, adjustment_version)

    def get_chart(
        self, symbol: str, interval: ChartInterval, start: int | None, end: int | None,
        limit: int, cursor: int | None = None,
    ) -> ChartHistory:
        if cursor is not None:
            end = cursor if end is None else min(end, cursor)
        if start is not None and end is not None and start >= end:
            raise UnsupportedMarketData("开始时间必须早于结束时间")

        history = self.get_history(symbol, "day" if interval == "1d" else interval, start, end, limit)
        oldest = history.bars[0].timestamp
        next_cursor = oldest if len(history.bars) == limit and (start is None or oldest > start) else None
        return ChartHistory(history, next_cursor)
