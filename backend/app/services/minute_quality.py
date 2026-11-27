"""根据交易时段和日线校验 1 分钟行情快照。"""

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from math import isfinite

from app.core.exceptions import MarketDataError
from app.core.market_time import CHINA, market_at, required_minutes
from app.models.model import Candle
from app.models.model import MinuteQuality


from .kline_service import has_valid_ohlcv


class MinuteCoverageError(MarketDataError):
    def __init__(self, message: str, quality: MinuteQuality):
        super().__init__(message)
        self.quality = quality


def _valid(bar: Candle, day: Candle | None) -> bool:
    if (
        day is None or bar.adjustment != "none" or day.adjustment != "none"
        or bar.timestamp % 60 or bar.end_timestamp != bar.timestamp + 60
        or not has_valid_ohlcv(bar)
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
    if bar.volume == 0:
        return bar.amount == 0
    if bar.amount == 0:
        return False
    return bar.low - 0.0101 <= bar.amount / bar.volume <= bar.high + 0.0101


def quality_report(start: int, end: int, source: str | None) -> MinuteQuality:
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
) -> tuple[tuple[Candle, ...], MinuteQuality]:
    quality = quality_report(start, end, source)
    reference = {datetime.fromtimestamp(bar.timestamp, CHINA).date(): bar for bar in raw_daily}
    expected, optional = {}, set()
    for day in sessions:
        for regular in required_minutes(day):
            expected.update((stamp, day) for stamp in regular if start <= stamp < end)
        optional.update(
            stamp for stamp in (market_at(day, 14, 57), market_at(day, 14, 58)) if start <= stamp < end
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
        if start > market_at(day, 9, 30) or end < market_at(day, 15, 0):
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
