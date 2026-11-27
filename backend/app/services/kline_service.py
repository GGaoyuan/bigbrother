"""校验、缓存并生成图表 K 线。"""

import hashlib
from datetime import datetime
from math import isfinite

from app.core.cache import ExpiringCache
from app.core.exceptions import ProviderUnavailable, UnsupportedMarketData
from app.core.logger import log_provider, observe_provider
from app.core.market_time import CHINA, midnight
from app.core.symbols import stock_exchange
from app.models.model import (
    Adjustment, Candle, ChartHistory, ChartInterval, Interval, KlineHistory,
)
from app.models.provider import MarketDataProvider

from .adjustment_service import AdjustmentService


def has_valid_ohlcv(bar: Candle) -> bool:
    return (
        all(isfinite(price) for price in (bar.open, bar.high, bar.low, bar.close))
        and 0 < bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high
        and type(bar.volume) is int and bar.volume >= 0
        and (bar.amount is None or (isfinite(bar.amount) and bar.amount >= 0))
    )


class KlineService:
    def __init__(self, source: MarketDataProvider, adjustment: AdjustmentService):
        self.source = source
        self.adjustment = adjustment
        self.history_cache = ExpiringCache(256)
        self.adjusted_cache = ExpiringCache(256)

    @staticmethod
    def _validate_bars(
        bars: tuple[Candle, ...], start: int | None, end: int | None, limit: int, adjust: Adjustment,
    ) -> tuple[Candle, ...]:
        by_time = {}
        for bar in bars:
            if not has_valid_ohlcv(bar) or not 0 <= bar.timestamp < bar.end_timestamp or bar.adjustment != adjust:
                raise ProviderUnavailable("K 线包含非法时间、OHLC 或成交量")
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
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> KlineHistory:
        stock_exchange(symbol)

        source = self.source
        with observe_provider(
            source.name, "klines", symbol=symbol, version=source.version,
            interval=interval, adjust=adjust, start=start, end=end, limit=limit,
        ):
            key = (source.name, source.version, symbol, interval, adjust, start, end, limit)
            bars = self.history_cache.get(key)
            if bars is None:
                bars = self._validate_bars(
                    source.get_klines(symbol, interval, adjust, start, end, limit),
                    start, end, limit, adjust,
                )
                historic = end is not None and end <= midnight(datetime.now(CHINA).date())
                self.history_cache.put(key, bars, 1800 if historic and adjust == "none" else 30)
            else:
                log_provider("cache_hit", source.name, "klines", symbol=symbol, interval=interval)
            return KlineHistory(bars, source.name, source.version)

    def get_chart(
        self, symbol: str, interval: ChartInterval, start: int | None, end: int | None,
        limit: int, cursor: int | None = None,
    ) -> ChartHistory:
        if cursor is not None:
            end = cursor if end is None else min(end, cursor)
        if start is not None and end is not None and start >= end:
            raise UnsupportedMarketData("开始时间必须早于结束时间")

        raw_interval: Interval = "day" if interval == "1d" else interval
        raw = self.get_history(symbol, raw_interval, "none", start, end, limit)
        factors = self.adjustment.get_factors(symbol)
        bars = raw.bars
        revision = hashlib.sha256(repr(bars).encode()).hexdigest()
        key = (symbol, interval, raw.source, raw.source_version, revision, factors.version)
        adjusted = self.adjusted_cache.get(key)
        if adjusted is None:
            adjusted = tuple(factors.apply(bar) for bar in bars)
            self.adjusted_cache.put(key, adjusted, 1800)

        oldest = adjusted[0].timestamp
        next_cursor = oldest if len(adjusted) == limit and (start is None or oldest > start) else None
        return ChartHistory(
            KlineHistory(adjusted, raw.source, raw.source_version),
            factors.version, factors.source, next_cursor,
        )
