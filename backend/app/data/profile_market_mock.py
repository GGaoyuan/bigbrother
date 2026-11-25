"""Deterministic synthetic Shanghai-session candles and trades."""

from datetime import date, datetime, time, timedelta
from itertools import groupby
from math import sin
from random import Random
from typing import Literal, TypedDict
from zoneinfo import ZoneInfo


Period = Literal["day", "60m", "30m", "15m", "5m"]
Side = Literal["buy", "sell", "neutral"]


class Trade(TypedDict):
    time: int
    priceCents: int
    volume: int
    side: Side | None


class HistoryPoint(TypedDict):
    start: int
    end: int
    close: int


class Candle(HistoryPoint):
    open: int
    high: int
    low: int
    volume: int


SHANGHAI = ZoneInfo("Asia/Shanghai")
FIRST_DAY = date(2025, 11, 3)
LAST_DAY = date(2026, 11, 20)
DAY_SECONDS = 24 * 3600
SESSION_SECONDS = 2 * 3600
SESSION_STARTS = (9 * 3600 + 30 * 60, 13 * 3600)
SESSION_DAYS = tuple(
    day
    for offset in range((LAST_DAY - FIRST_DAY).days + 1)
    if (day := FIRST_DAY + timedelta(days=offset)).weekday() < 5
)
PERIOD_SECONDS = {"60m": 3600, "30m": 1800, "15m": 900, "5m": 300}
STOCK_NAMES = {
    "000001": "平安银行",
    "000858": "五粮液",
    "002594": "比亚迪",
    "300750": "宁德时代",
    "600036": "招商银行",
    "600519": "贵州茅台",
    "601318": "中国平安",
}
BASE_PRICES = {"000001": 1150, "600519": 148000}


def _day_start(day: date) -> int:
    return int(datetime.combine(day, time.min, tzinfo=SHANGHAI).timestamp())


def _day_trades(code: str, day: date, day_start: int) -> list[Trade]:
    offset = (day - FIRST_DAY).days
    symbol = int(code)
    random = Random(symbol * 1000 + offset)
    base = BASE_PRICES.get(code, 1500 + symbol % 6500)
    trend = round(0.31 * offset + 96 * sin(offset / 22 + symbol % 29))
    price = base + trend
    trades: list[Trade] = []

    for session in SESSION_STARTS:
        for interval in range(0, SESSION_SECONDS, PERIOD_SECONDS["5m"]):
            for position in (0, 65, 152, 249):
                change = random.randint(-13, 13)
                price = max(1, price + change)
                side: Side = "neutral"
                if change > 0:
                    side = "buy"
                elif change < 0:
                    side = "sell"
                trades.append({
                    "time": day_start + session + interval + position,
                    "priceCents": price,
                    "volume": random.randint(1, 250) * 100,
                    "side": side,
                })

    return trades


def _candle(trades: list[Trade], start: int, end: int) -> Candle:
    prices = [trade["priceCents"] for trade in trades]
    return {
        "start": start,
        "end": end,
        "open": prices[0],
        "high": max(prices),
        "low": min(prices),
        "close": prices[-1],
        "volume": sum(trade["volume"] for trade in trades),
    }


def _intraday_candles(trades: list[Trade], day_start: int, seconds: int) -> list[Candle]:
    afternoon = day_start + SESSION_STARTS[1]
    morning = day_start + SESSION_STARTS[0]

    def interval_start(trade: Trade) -> int:
        timestamp = trade["time"]
        session = morning if timestamp < afternoon else afternoon
        return session + (timestamp - session) // seconds * seconds

    return [
        _candle(list(interval_trades), start, start + seconds)
        for start, interval_trades in groupby(trades, key=interval_start)
    ]


def get_history(code: str, period: Period) -> tuple[list[Candle], list[HistoryPoint]]:
    """Build period candles and the full-resolution daily overview for a code."""
    bars: list[Candle] = []
    overview: list[HistoryPoint] = []
    for day in SESSION_DAYS:
        start = _day_start(day)
        trades = _day_trades(code, day, start)
        daily = _candle(trades, start, start + DAY_SECONDS)
        overview.append({
            "start": daily["start"],
            "end": daily["end"],
            "close": daily["close"],
        })
        if period == "day":
            bars.append(daily)
        else:
            bars.extend(_intraday_candles(trades, start, PERIOD_SECONDS[period]))
    return bars, overview


def get_trades(code: str, start: int, end: int) -> list[Trade]:
    """Generate synthetic ticks only for fixture sessions overlapping [start, end)."""
    trades: list[Trade] = []
    for day in SESSION_DAYS:
        session_start = _day_start(day)
        if session_start >= end:
            break
        if session_start + DAY_SECONDS <= start:
            continue
        trades.extend(
            trade
            for trade in _day_trades(code, day, session_start)
            if start <= trade["time"] < end
        )
    return trades
