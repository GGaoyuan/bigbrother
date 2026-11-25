"""Normalize recent native Sina one-minute A-share candles through AKShare."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from math import isfinite

from akshare import __version__ as AKSHARE_VERSION
from akshare import stock_zh_a_minute
from pandas import DataFrame

from app.data.stock_market_types import (
    Adjustment,
    Candle,
    Interval,
    ProviderUnavailable,
    UnsupportedMarketData,
    candle_span,
    stock_exchange,
)


def _native_candle(row: dict[str, object]) -> Candle:
    label = datetime.fromisoformat(str(row["day"]))
    if label.second or label.microsecond:
        raise ProviderUnavailable("新浪 1 分钟 K 线时间标签未对齐到分钟")
    timestamp, end_timestamp = candle_span(label, "1m", right_labeled=True)

    opening, high, low, close = (float(str(row[field])) for field in ("open", "high", "low", "close"))
    if not all(isfinite(price) for price in (opening, high, low, close)) or not (
        0 < low <= min(opening, close) <= max(opening, close) <= high
    ):
        raise ProviderUnavailable("新浪 1 分钟 K 线价格异常")

    try:
        raw_volume = Decimal(str(row["volume"]))
    except InvalidOperation as exc:
        raise ProviderUnavailable("新浪 1 分钟 K 线成交量格式异常") from exc
    if not raw_volume.is_finite() or raw_volume < 0 or raw_volume != raw_volume.to_integral_value():
        raise ProviderUnavailable("新浪 1 分钟 K 线成交量不是有效的股数")
    volume = int(raw_volume)

    raw_amount = row.get("amount")
    amount = float(str(raw_amount)) if raw_amount not in (None, "") else None
    if amount is not None and (not isfinite(amount) or amount < 0):
        raise ProviderUnavailable("新浪 1 分钟 K 线成交额异常")

    return Candle(
        timestamp=timestamp,
        end_timestamp=end_timestamp,
        open=opening,
        high=high,
        low=low,
        close=close,
        volume=volume,
        amount=amount,
        original_volume_unit="shares",
        original_volume=volume,
    )


class SinaMinuteProvider:
    name = "akshare-sina"
    version = f"{AKSHARE_VERSION}-sina-minute-v1"

    def get_klines(
        self,
        symbol: str,
        interval: Interval,
        adjust: Adjustment,
        start: int | None,
        end: int | None,
        limit: int,
    ) -> tuple[Candle, ...]:
        """Load native 1m candles for the stock and clip the available time range."""
        if interval != "1m" or adjust != "none":
            raise UnsupportedMarketData("新浪分钟适配器仅提供不复权 1 分钟 K 线")
        exchange = stock_exchange(symbol)
        if exchange == "BSE":
            raise UnsupportedMarketData("新浪分钟适配器未验证北交所 A 股")
        if limit < 1 or (start is not None and end is not None and start >= end):
            raise UnsupportedMarketData("新浪 1 分钟 K 线区间或条数无效")

        prefix = "sh" if exchange == "SSE" else "sz"
        try:
            frame = stock_zh_a_minute(symbol=f"{prefix}{symbol}", period="1", adjust="")
        except Exception as exc:
            raise ProviderUnavailable("新浪 1 分钟行情暂不可用") from exc
        if not isinstance(frame, DataFrame) or frame.empty:
            raise ProviderUnavailable("新浪未返回可用的 1 分钟 K 线")

        try:
            bars = [_native_candle(row) for row in frame.to_dict("records")]
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderUnavailable("新浪 1 分钟 K 线字段异常") from exc
        # Keep native duplicate records for the consumer's coverage validation.
        clipped = (
            bar for bar in bars
            if (start is None or bar.end_timestamp > start) and (end is None or bar.timestamp < end)
        )
        return tuple(sorted(clipped, key=lambda bar: bar.timestamp)[-limit:])
