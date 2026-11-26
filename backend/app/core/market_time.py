"""Beijing time and A-share session boundaries."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


CHINA = ZoneInfo("Asia/Shanghai")
MINUTES = {"1m": 1, "5m": 5, "60m": 60}


def midnight(day: date) -> int:
    return int(datetime.combine(day, time(), CHINA).timestamp())


def candle_span(
    stamp: date | datetime, interval: str, *, right_labeled: bool = False,
) -> tuple[int, int]:
    """Convert a Chinese trading label to a half-open interval."""
    if isinstance(stamp, datetime):
        stamp = stamp.astimezone(CHINA) if stamp.tzinfo else stamp.replace(tzinfo=CHINA)
        day = stamp.date()
    else:
        day = stamp
    if interval in MINUTES:
        if not isinstance(stamp, datetime):
            raise ValueError("分钟 K 线缺少时分")
        duration = timedelta(minutes=MINUTES[interval])
        start, end = (stamp - duration, stamp) if right_labeled else (stamp, stamp + duration)
        return int(start.timestamp()), int(end.timestamp())
    if interval == "week":
        start = day - timedelta(days=day.weekday())
        return midnight(start), midnight(start + timedelta(days=7))
    if interval == "month":
        start = day.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
        return midnight(start), midnight(end)
    return midnight(day), midnight(day + timedelta(days=1))


def minute_window(start: int, end: int) -> tuple[int, int]:
    """Include whole bars that overlap the selected half-open interval."""
    return start // 60 * 60, (end + 59) // 60 * 60


def market_at(day: date, hour: int, minute: int) -> int:
    return int(datetime.combine(day, time(hour, minute), CHINA).timestamp())


def required_minutes(day: date) -> tuple[range, ...]:
    # The closing cross executes at 15:00. Providers can omit the two minutes
    # before that cross. A native bar inside those minutes is allowed and kept.
    return (
        range(market_at(day, 9, 30), market_at(day, 11, 30), 60),
        range(market_at(day, 13, 0), market_at(day, 14, 57), 60),
        range(market_at(day, 14, 59), market_at(day, 15, 0), 60),
    )


def has_trading_minutes(start: int, end: int, sessions: tuple[date, ...]) -> bool:
    return any(
        window.start < end and window.stop > start
        for day in sessions for window in required_minutes(day)
    )
