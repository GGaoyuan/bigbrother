"""北京时间与 A 股交易时段边界。"""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


CHINA = ZoneInfo("Asia/Shanghai")
MINUTES = {"1m": 1, "5m": 5, "60m": 60}


def midnight(day: date) -> int:
    return int(datetime.combine(day, time(), CHINA).timestamp())


def candle_span(stamp: datetime, interval: str) -> tuple[int, int]:
    """将日线交易日或分钟线结束时间转换为左闭右开的区间。"""
    stamp = stamp.astimezone(CHINA) if stamp.tzinfo else stamp.replace(tzinfo=CHINA)
    if interval == "1d":
        day = stamp.date()
        return midnight(day), midnight(day + timedelta(days=1))
    duration = timedelta(minutes=MINUTES[interval])
    return int((stamp - duration).timestamp()), int(stamp.timestamp())


def minute_window(start: int, end: int) -> tuple[int, int]:
    """完整纳入与左闭右开选区相交的分钟 K 线。"""
    return start // 60 * 60, (end + 59) // 60 * 60


def market_at(day: date, hour: int, minute: int) -> int:
    return int(datetime.combine(day, time(hour, minute), CHINA).timestamp())


def required_minutes(day: date) -> tuple[range, ...]:
    # 收盘集合竞价在 15:00 撮合。行情源可能省略撮合前的两个分钟档，
    # 行情源实际返回的原生分钟 K 线可以纳入统计。
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
