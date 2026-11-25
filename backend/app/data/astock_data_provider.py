"""A-stock-data fallback for Tencent candlesticks and approximate latest trades."""

from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from math import isfinite

from app.data.stock_adjustment import AdjustmentFactors
from app.data.stock_market_types import (
    CHINA,
    MINUTES,
    Adjustment,
    Candle,
    Interval,
    ProviderUnavailable,
    StockInfo,
    StockNotFound,
    Tick,
    TickCoverage,
    TickDay,
    UnsupportedMarketData,
    candle_span,
    stock_board,
    stock_exchange,
)
from app.data.vendor import astock_tencent as tencent


_PREFIX = {"SSE": "sh", "SZSE": "sz", "BSE": "bj"}
_SIDE = {"B": "BUY", "S": "SELL", "M": "UNKNOWN"}
_TICK_RESOLUTION = "aggregated_3s"
_TICK_LIMITATION = "腾讯仅提供最近一个交易日的约 3 秒合并成交，无法按价位核验逐笔量价"
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
    _latest_tick_day(key)
    raise ProviderUnavailable(f"腾讯股票名称响应不完整：{symbol}")


def _tencent_equity_symbol(symbol: str) -> str:
    exchange = stock_exchange(symbol)
    if exchange == "BSE":
        raise UnsupportedMarketData("a-stock-data 的腾讯数据不支持北交所 K 线和逐笔")
    return _PREFIX[exchange] + symbol


def _latest_tick_day(key: str) -> date:
    try:
        try:
            day, _, _, _ = tencent._tencent_qt_snapshot(key)
        except ValueError as exc:
            if str(exc) == f"腾讯没有 {key} 这个代码":
                raise StockNotFound(str(exc)) from exc
            raise
        return date.fromisoformat(day)
    except _UPSTREAM_ERRORS as exc:
        raise ProviderUnavailable(f"a-stock-data 腾讯成交日期不可用：{exc}") from exc


class AStockDataProvider:
    name = "a-stock-data"
    version = "3.10.4+f215349-v2"

    def get_stock_info(self, symbol: str) -> StockInfo:
        exchange = stock_exchange(symbol)
        return StockInfo(symbol, _stock_name(symbol, exchange), exchange, stock_board(symbol))

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
        unit = "shares" if symbol.startswith(("688", "689")) else "lots"
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
                )
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

    def get_adjustment_factors(self, symbol: str) -> AdjustmentFactors:
        raise UnsupportedMarketData("腾讯此接口未提供可统一应用至所有周期的前复权因子")

    def get_ticks(self, symbol: str, day: date) -> TickDay:
        key = _tencent_equity_symbol(symbol)
        available = _latest_tick_day(key)
        if day != available:
            raise UnsupportedMarketData(f"{_TICK_LIMITATION}，当前源日期为 {available.isoformat()}")

        ticks: list[Tick] = []
        omitted_zero_lot_rows = 0
        try:
            frame = tencent.tencent_ticks(key)
            for row in frame.to_dict(orient="records"):
                if row["date"] != day.isoformat() or row["code"] != key:
                    raise RuntimeError("成交期间源交易日或股票代码与请求不一致")
                timestamp = datetime.fromisoformat(f"{row['date']}T{row['time']}").replace(tzinfo=CHINA)
                volume = _shares(row["volume"], "lots")
                if volume == 0:
                    omitted_zero_lot_rows += 1
                    continue
                ticks.append(Tick(
                    timestamp=int(timestamp.timestamp()),
                    price=_price(row["price"]),
                    volume=volume,
                    amount=float(row["amount"]),
                    side=_SIDE[row["side"]],
                ))
        except _UPSTREAM_ERRORS as exc:
            raise ProviderUnavailable(f"a-stock-data 腾讯成交分笔不可用：{exc}") from exc

        complete = bool(ticks) and frame.attrs.get("complete") is True and not frame.attrs.get("missing_seq")
        reason = _TICK_LIMITATION
        unit = "lots"
        if symbol.startswith(("688", "689")):
            reason += "。科创板分笔成交量已按手取整"
            unit = "rounded_lots"
        if not complete:
            reason += "。源未通过全天完整性核验"
        if omitted_zero_lot_rows:
            reason += f"。省略了 {omitted_zero_lot_rows} 条原始手数为零的记录"
        return TickDay(
            day, tuple(ticks), complete, _TICK_RESOLUTION, unit, False, reason,
            omitted_zero_lot_rows=omitted_zero_lot_rows,
        )

    def get_tick_coverage(self, symbol: str) -> TickCoverage:
        if stock_exchange(symbol) == "BSE":
            return TickCoverage(None, None, False, False, False, False, _TICK_RESOLUTION, "腾讯不支持北交所逐笔")
        day = _latest_tick_day(_tencent_equity_symbol(symbol))
        return TickCoverage(day, day, None, False, True, False, _TICK_RESOLUTION, _TICK_LIMITATION)

    def health_check(self) -> bool:
        try:
            self.get_stock_info("600519")
        except (StockNotFound, ProviderUnavailable):
            return False
        return True
