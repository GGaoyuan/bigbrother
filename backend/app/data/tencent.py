"""A-stock-data fallback for Tencent stock names and candlesticks."""

from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from math import isfinite

from app.core.exceptions import ProviderUnavailable, StockNotFound, UnsupportedMarketData
from app.core.market_time import CHINA, MINUTES, candle_span
from app.core.symbols import stock_board, stock_exchange
from app.models.kline import Adjustment, Candle, Interval, VolumeUnit
from app.models.stock import StockInfo
from app.data.vendor import astock_tencent as tencent


_PREFIX = {"SSE": "sh", "SZSE": "sz", "BSE": "bj"}
_SOURCE = "a-stock-data"
_VERSION = "3.10.4+f215349-v2"
_MINUTE_HISTORY_LIMIT = 320
_MINUTE_HISTORY_ERROR = "a-stock-data 的腾讯分钟 K 线只覆盖最近 320 根，所请求区间超出覆盖范围"
_UPSTREAM_ERRORS = (RuntimeError, ValueError, OSError, TypeError, KeyError, OverflowError)


def _adjustment(interval: Interval, adjust: Adjustment) -> str:
    if interval in MINUTES and adjust != "none":
        raise UnsupportedMarketData("a-stock-data 的腾讯分钟 K 线仅支持不复权")
    return "" if adjust == "none" else adjust


def _date_options(interval: Interval, start: int | None, end: int | None, limit: int) -> dict:
    if interval in MINUTES:
        return {"count": _MINUTE_HISTORY_LIMIT if start is not None or end is not None else limit}
    if start is None and end is None and limit <= 640:
        return {"count": limit}

    # Tencent only accepts end with start. Allow enough calendar days to obtain the requested bars.
    last = datetime.fromtimestamp(end - 1, CHINA).date() if end is not None else datetime.now(CHINA).date()
    if start is not None:
        first = datetime.fromtimestamp(start, CHINA).date()
    else:
        days_per_bar = {"day": 2, "week": 8, "month": 32}[interval]
        first = last - timedelta(days=limit * days_per_bar)
    if interval in ("week", "month"):
        first = datetime.fromtimestamp(candle_span(first, interval)[0], CHINA).date()
        last = datetime.fromtimestamp(candle_span(last, interval)[1] - 1, CHINA).date()
    return {"start": first.isoformat(), "end": last.isoformat()}


def _shares(raw, unit: str) -> int:
    try:
        shares = Decimal(str(raw)) * (100 if unit == "lots" else 1)
    except InvalidOperation as exc:
        raise ProviderUnavailable("腾讯返回无效成交量") from exc
    if not shares.is_finite() or shares < 0 or shares != shares.to_integral_value():
        raise ProviderUnavailable("腾讯成交量不能转换成整股")
    return int(shares)


def _price(value) -> float:
    price = float(value)
    if not isfinite(price) or price <= 0:
        raise ProviderUnavailable("腾讯返回无效价格")
    return price


def _stock_name(symbol: str, exchange: str) -> str:
    key = _PREFIX[exchange] + symbol
    try:
        quotes = tencent.tencent_quote([key])
    except _UPSTREAM_ERRORS as exc:
        raise ProviderUnavailable(f"a-stock-data 腾讯股票信息不可用：{exc}") from exc
    quote = quotes.get(key) if isinstance(quotes, dict) else None
    name = quote.get("name") if isinstance(quote, dict) else None
    if isinstance(name, str) and name.strip():
        return name.strip()

    # The quote parser drops short records. Only a confirmed no-match is a 404.
    _check_quote_exists(key)
    raise ProviderUnavailable(f"腾讯股票名称响应不完整：{symbol}")


def _tencent_equity_symbol(symbol: str) -> str:
    exchange = stock_exchange(symbol)
    if exchange == "BSE":
        raise UnsupportedMarketData("a-stock-data 的腾讯数据不支持北交所 K 线")
    return _PREFIX[exchange] + symbol


def _check_quote_exists(key: str) -> None:
    try:
        try:
            day, _, _, _ = tencent._tencent_qt_snapshot(key)
        except ValueError as exc:
            if str(exc) == f"腾讯没有 {key} 这个代码":
                raise StockNotFound(str(exc)) from exc
            raise
        date.fromisoformat(day)
    except _UPSTREAM_ERRORS as exc:
        raise ProviderUnavailable(f"a-stock-data 腾讯成交日期不可用：{exc}") from exc


class TencentStockData:
    name = _SOURCE
    version = _VERSION

    def get_stock_info(self, symbol: str) -> StockInfo:
        exchange = stock_exchange(symbol)
        return StockInfo(symbol, _stock_name(symbol, exchange), exchange, stock_board(symbol))


class TencentKlineData:
    name = _SOURCE
    version = _VERSION
    minute_history_limit: int | None = _MINUTE_HISTORY_LIMIT

    def get_klines(
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]:
        if limit < 1 or (start is not None and end is not None and start >= end):
            raise UnsupportedMarketData("K 线条数和时间区间必须有效")
        key = _tencent_equity_symbol(symbol)
        adjustment = _adjustment(interval, adjust)
        minute = interval in MINUTES
        if minute and start is None and limit > _MINUTE_HISTORY_LIMIT:
            raise UnsupportedMarketData(_MINUTE_HISTORY_ERROR)
        tencent_period = f"m{MINUTES[interval]}" if minute else interval
        unit: VolumeUnit = "shares" if symbol.startswith(("688", "689")) else "lots"
        candles: dict[int, Candle] = {}
        now = int(datetime.now(CHINA).timestamp())
        try:
            options = _date_options(interval, start, end, limit)
            frame = tencent.tencent_kline(key, period=tencent_period, adjust=adjustment, **options)
            for row in frame.to_dict(orient="records"):
                label = (
                    datetime.fromisoformat(row["datetime"]) if minute
                    else date.fromisoformat(row["date"])
                )
                opened, closed = candle_span(label, interval, right_labeled=minute)
                if opened > now:
                    continue
                candle = Candle(
                    timestamp=opened,
                    end_timestamp=closed,
                    open=_price(row["open"]),
                    high=_price(row["high"]),
                    low=_price(row["low"]),
                    close=_price(row["close"]),
                    volume=_shares(row["volume"], unit),
                    amount=None,
                    original_volume_unit=unit,
                    original_volume=float(row["volume"]),
                    adjustment=adjust,
                )
                if not candle.has_valid_ohlcv():
                    raise ProviderUnavailable("腾讯 K 线开高低收顺序异常")
                if opened in candles and candles[opened] != candle:
                    raise RuntimeError("腾讯 K 线包含冲突的重复时间")
                candles[opened] = candle
        except _UPSTREAM_ERRORS as exc:
            raise ProviderUnavailable(f"a-stock-data 腾讯 K 线不可用：{exc}") from exc

        ordered = [candles[stamp] for stamp in sorted(candles)]
        if not ordered:
            raise ProviderUnavailable("腾讯 K 线没有可用数据")
        if minute and unit == "lots":
            latest_day = datetime.fromtimestamp(ordered[-1].timestamp, CHINA).date()
            latest_start = candle_span(latest_day, "day")[0]
            latest = [bar for bar in ordered if bar.timestamp >= latest_start]
            if all(bar.volume % 100 == 0 for bar in latest):
                ordered = [
                    replace(bar, original_volume_unit="rounded_lots") if bar.timestamp >= latest_start else bar
                    for bar in ordered
                ]
        first = ordered[0].timestamp
        if minute and ((start is not None and start < first) or (end is not None and end <= first)):
            raise UnsupportedMarketData(_MINUTE_HISTORY_ERROR)
        in_range = [
            candle for candle in ordered
            if (start is None or candle.end_timestamp > start) and (end is None or candle.timestamp < end)
        ]
        if (minute and start is None and end is not None and len(ordered) >= _MINUTE_HISTORY_LIMIT
                and len(in_range) < limit):
            raise UnsupportedMarketData(_MINUTE_HISTORY_ERROR)
        return tuple(in_range[-limit:])
