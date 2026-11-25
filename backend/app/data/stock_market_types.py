"""Normalized contracts for A-share providers. Prices are CNY and volume is shares."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING, Literal, Protocol
from zoneinfo import ZoneInfo


if TYPE_CHECKING:
    from app.data.stock_adjustment import AdjustmentFactors


CHINA = ZoneInfo("Asia/Shanghai")
Interval = Literal["day", "week", "month", "1m", "5m", "60m"]
Adjustment = Literal["none", "qfq", "hfq"]
MINUTES = {"1m": 1, "5m": 5, "60m": 60}


class MarketDataError(Exception):
    status_code = 502


class ProviderUnavailable(MarketDataError):
    pass


class UnsupportedMarketData(MarketDataError):
    status_code = 422


class StockNotFound(MarketDataError):
    status_code = 404


class TickCoverageError(MarketDataError):
    status_code = 409


class MinuteCoverageError(MarketDataError):
    status_code = 409

    def __init__(self, message: str, quality: dict):
        super().__init__(message)
        self.quality = quality


@dataclass(frozen=True, slots=True)
class StockInfo:
    symbol: str
    name: str
    exchange: str
    market: str
    currency: str = "CNY"
    price_tick: float = 0.01


@dataclass(frozen=True, slots=True)
class Candle:
    timestamp: int
    end_timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float | None
    original_volume_unit: str
    original_volume: int | float | None = None
    volume_precision_shares: int = 1


@dataclass(frozen=True, slots=True)
class Tick:
    timestamp: int
    price: float
    volume: int
    amount: float | None
    side: Literal["BUY", "SELL", "UNKNOWN"]
    trade_id: str | None = None


@dataclass(frozen=True, slots=True)
class TickDay:
    day: date
    ticks: tuple[Tick, ...]
    complete: bool
    resolution: str
    original_volume_unit: str
    price_volume_exact: bool
    reason: str | None = None
    omitted_zero_lot_rows: int = 0
    verified_until: int | None = None  # Exclusive. None means no partial coverage bound.


@dataclass(frozen=True, slots=True)
class TickCoverage:
    start: date | None
    end: date | None
    complete: bool | None
    history_supported: bool
    has_direction: bool
    covers_bse: bool
    resolution: str
    reason: str | None = None


class MarketDataProvider(Protocol):
    name: str
    version: str

    def get_stock_info(self, symbol: str) -> StockInfo: ...

    def get_klines(
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]: ...

    def get_adjustment_factors(self, symbol: str) -> "AdjustmentFactors": ...

    def get_ticks(self, symbol: str, day: date) -> TickDay: ...

    def get_tick_coverage(self, symbol: str) -> TickCoverage: ...

    def health_check(self) -> bool: ...


def stock_exchange(symbol: str) -> str:
    if len(symbol) != 6 or not symbol.isascii() or not symbol.isdigit():
        raise StockNotFound("请输入六位 A 股代码")
    if symbol.startswith(("600", "601", "603", "605", "688", "689")):
        return "SSE"
    if symbol.startswith(("000", "001", "002", "003", "300", "301")):
        return "SZSE"
    if symbol.startswith(("4", "8", "920")):
        return "BSE"
    raise StockNotFound(f"{symbol} 不属于支持的 A 股代码段")


def stock_board(symbol: str) -> str:
    if stock_exchange(symbol) == "BSE":
        return "北交所"
    if symbol.startswith(("688", "689")):
        return "科创板"
    if symbol.startswith(("300", "301")):
        return "创业板"
    return "主板"


def midnight(day: date) -> int:
    return int(datetime.combine(day, time(), CHINA).timestamp())


def candle_span(
    stamp: date | datetime, interval: Interval, *, right_labeled: bool = False,
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
