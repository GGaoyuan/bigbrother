"""Shanghai session boundaries and validation of a single raw minute snapshot."""

from collections import defaultdict
from datetime import date, datetime, time
from decimal import Decimal
from math import isfinite

from app.data.stock_market_types import CHINA, Candle, MinuteCoverageError, ProviderUnavailable


def exchange_calendar() -> tuple[date, ...]:
    import akshare as ak

    try:
        rows = tuple(ak.tool_trade_date_hist_sina()["trade_date"])
    except (KeyError, TypeError, ValueError, OSError, RuntimeError) as exc:
        raise ProviderUnavailable("交易日历暂不可用") from exc
    if not rows or any(type(day) is not date for day in rows) or rows != tuple(sorted(set(rows))):
        raise ProviderUnavailable("交易日历返回日期无效")
    return rows


def minute_window(start: int, end: int) -> tuple[int, int]:
    """Include whole bars that overlap the selected half-open interval."""
    return start // 60 * 60, (end + 59) // 60 * 60


def _at(day: date, hour: int, minute: int) -> int:
    return int(datetime.combine(day, time(hour, minute), CHINA).timestamp())


def _minutes(day: date) -> tuple[range, ...]:
    # The closing cross executes at 15:00. Providers can omit the two minutes
    # before that cross. A native bar inside those minutes is allowed and kept.
    return (
        range(_at(day, 9, 30), _at(day, 11, 30), 60),
        range(_at(day, 13, 0), _at(day, 14, 57), 60),
        range(_at(day, 14, 59), _at(day, 15, 0), 60),
    )


def has_trading_minutes(start: int, end: int, sessions: tuple[date, ...]) -> bool:
    return any(
        window.start < end and window.stop > start
        for day in sessions for window in _minutes(day)
    )


def _valid(bar: Candle, day: Candle | None) -> bool:
    if (
        day is None or bar.timestamp % 60 or bar.end_timestamp != bar.timestamp + 60
        or not all(isfinite(price) for price in (bar.open, bar.high, bar.low, bar.close))
        or not 0 < bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high
        or type(bar.volume) is not int or bar.volume < 0
        or bar.volume_precision_shares not in (1, 100) or bar.volume % bar.volume_precision_shares
        or bar.original_volume_unit not in ("lots", "shares")
        or bar.original_volume is None or not isfinite(bar.original_volume) or bar.original_volume < 0
        or bar.low < day.low - 0.0101 or bar.high > day.high + 0.0101
    ):
        return False
    multiplier = 100 if bar.original_volume_unit == "lots" else 1
    if Decimal(str(bar.original_volume)) * multiplier != bar.volume:
        return False
    if bar.amount is None:
        return True
    if not isfinite(bar.amount) or bar.amount < 0:
        return False
    if bar.volume == 0:
        return bar.amount == 0
    if bar.amount == 0:
        return False
    return bar.low - 0.0101 <= bar.amount / bar.volume <= bar.high + 0.0101


def quality_report(start: int, end: int, source: str | None) -> dict:
    return {
        "requested_start": start, "requested_end": end,
        "aligned_start": start, "aligned_end": end,
        "actual_start": None, "actual_end": None, "available_start": None, "available_end": None,
        "trading_day_count": 0, "minute_count": 0, "duplicate_count": 0, "invalid_count": 0,
        "missing_minute_count": None, "missing": [], "daily_mismatches": [], "source": source,
        "factor_complete": False, "complete": False, "volume_precision_shares": None,
    }


def validate_minutes(
    bars: tuple[Candle, ...], start: int, end: int, sessions: tuple[date, ...],
    raw_daily: tuple[Candle, ...], source: str, *, closed_until: int | None = None,
) -> tuple[tuple[Candle, ...], dict]:
    quality = quality_report(start, end, source)
    reference = {datetime.fromtimestamp(bar.timestamp, CHINA).date(): bar for bar in raw_daily}
    expected, optional = {}, set()
    for day in sessions:
        for regular in _minutes(day):
            expected.update((stamp, day) for stamp in regular if start <= stamp < end)
        optional.update(
            stamp for stamp in (_at(day, 14, 57), _at(day, 14, 58)) if start <= stamp < end
        )

    if bars:
        quality["available_start"] = min(bar.timestamp for bar in bars)
        quality["available_end"] = max(bar.end_timestamp for bar in bars)
    if not expected:
        raise MinuteCoverageError("所选区间没有交易分钟", quality)

    selected: dict[int, Candle] = {}
    seen = set()
    for bar in bars:
        stamp = bar.timestamp
        if not start <= stamp < end:
            continue
        if stamp in seen:
            quality["duplicate_count"] += 1
            continue
        seen.add(stamp)
        day = datetime.fromtimestamp(stamp, CHINA).date()
        if (
            (stamp not in expected and stamp not in optional)
            or not _valid(bar, reference.get(day))
            or (closed_until is not None and bar.end_timestamp > closed_until)
        ):
            quality["invalid_count"] += 1
            continue
        selected[stamp] = bar

    missing_by_day: dict[date, list[int]] = {}
    for stamp, day in expected.items():
        if stamp not in selected:
            missing_by_day.setdefault(day, []).append(stamp)
    rows = tuple(selected[stamp] for stamp in sorted(selected))
    if rows:
        quality["actual_start"] = rows[0].timestamp
        quality["actual_end"] = rows[-1].end_timestamp
    quality["missing"] = [
        {
            "date": day.isoformat(), "count": len(stamps), "first": stamps[0], "last": stamps[-1],
            "daily_reference_missing": day not in reference,
        }
        for day, stamps in missing_by_day.items()
    ]
    quality["minute_count"] = len(rows)
    if rows:
        quality["volume_precision_shares"] = max(bar.volume_precision_shares for bar in rows)
    quality["trading_day_count"] = len({datetime.fromtimestamp(bar.timestamp, CHINA).date() for bar in rows})
    quality["missing_minute_count"] = sum(len(stamps) for stamps in missing_by_day.values())
    if quality["duplicate_count"] or quality["invalid_count"] or quality["missing_minute_count"]:
        raise MinuteCoverageError(
            "所选区间的 1 分钟 K 线不足或未通过质量核验", quality,
        )
    by_day = defaultdict(list)
    for bar in rows:
        by_day[datetime.fromtimestamp(bar.timestamp, CHINA).date()].append(bar)
    for day, day_rows in by_day.items():
        if start > _at(day, 9, 30) or end < _at(day, 15, 0):
            continue
        daily = reference[day]
        volume = sum(bar.volume for bar in day_rows)
        tolerance = max(bar.volume_precision_shares for bar in day_rows) - 1
        if daily.original_volume_unit in ("lots", "rounded_lots"):
            tolerance = max(tolerance, 99)
        day_prices = (day_rows[0].open, max(bar.high for bar in day_rows),
                      min(bar.low for bar in day_rows), day_rows[-1].close)
        reference_prices = (daily.open, daily.high, daily.low, daily.close)
        if abs(volume - daily.volume) > tolerance or any(
            abs(given - expected) > 0.0101 for given, expected in zip(day_prices, reference_prices)
        ):
            quality["daily_mismatches"].append(day.isoformat())
    if quality["daily_mismatches"]:
        raise MinuteCoverageError("整日分钟 K 线的股数或价格与不复权日线不符", quality)
    quality["complete"] = True
    return rows, quality
