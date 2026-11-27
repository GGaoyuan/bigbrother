"""定义后端使用的数据字段。"""

from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction
from typing import Literal, TypedDict


Interval = Literal["day", "week", "month", "1m", "5m", "60m"]
ChartInterval = Literal["1d", "60m", "5m"]
Adjustment = Literal["none", "qfq", "hfq"]
VolumeUnit = Literal["shares", "lots", "rounded_lots", "unknown"]


@dataclass(frozen=True, slots=True)
class Candle:
    """使用北京时间交易时段，时间戳以 Unix 秒表示，区间左闭右开。

    价格单位为元，默认不复权。成交量单位为股，成交额单位为元。
    成交额无法可靠取得时为 None，原始成交量亦可缺省，原始单位可为未知。
    成交量精度表示行情源公布的股数粒度，原始单位另行记录。
    """

    timestamp: int
    end_timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float | None
    original_volume_unit: VolumeUnit
    original_volume: int | float | None = None
    volume_precision_shares: int = 1
    adjustment: Adjustment = field(default="none", repr=False)


@dataclass(frozen=True, slots=True)
class KlineHistory:
    bars: tuple[Candle, ...]
    source: str
    source_version: str


@dataclass(frozen=True, slots=True)
class ChartHistory:
    history: KlineHistory
    adjustment_version: str
    adjustment_source: str
    next_cursor: int | None


@dataclass(frozen=True, slots=True)
class StockInfo:
    symbol: str
    name: str
    exchange: str
    market: str
    currency: str = "CNY"
    price_tick: float = 0.01


@dataclass(frozen=True, slots=True)
class StockLookup:
    stock: StockInfo
    source: str
    source_version: str
    available_sources: tuple[str, ...]
    configured_sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CorporateAction:
    """现金红利按除权前每 10 股计，单位为元。送转和配股按每 10 股计，配股价格单位为元每股。"""

    ex_date: date
    cash_dividend: Fraction
    bonus_shares: Fraction
    rights_shares: Fraction
    rights_price: Fraction


@dataclass(frozen=True, slots=True)
class TradingCalendar:
    """定义含首尾日期的日历覆盖范围，以及按升序排列的实际交易日。"""

    start: date
    end: date
    sessions: tuple[date, ...]


class MissingMinutes(TypedDict):
    date: str
    count: int
    first: int
    last: int
    daily_reference_missing: bool


class SourceFailure(TypedDict):
    source: str
    message: str


class _OptionalQuality(TypedDict, total=False):
    source_errors: list[SourceFailure]


class MinuteQuality(_OptionalQuality):
    requested_start: int
    requested_end: int
    aligned_start: int
    aligned_end: int
    actual_start: int | None
    actual_end: int | None
    available_start: int | None
    available_end: int | None
    trading_day_count: int
    minute_count: int
    duplicate_count: int
    invalid_count: int
    missing_minute_count: int | None
    missing: list[MissingMinutes]
    daily_mismatches: list[str]
    source: str | None
    factor_complete: bool
    complete: bool
    volume_precision_shares: int | None


@dataclass(frozen=True, slots=True)
class PriceLevel:
    price_cents: int
    low_price_cents: int
    high_price_cents: int
    volume: int
    node: Literal["HVN", "LVN"] | None


@dataclass(frozen=True, slots=True)
class ValueArea:
    low_cents: int
    high_cents: int
    volume: int


@dataclass(frozen=True, slots=True)
class VolumeDistribution:
    step_cents: int
    levels: tuple[PriceLevel, ...]
    total_volume: int
    poc: PriceLevel | None = None
    value_area: ValueArea | None = None


@dataclass(frozen=True, slots=True)
class VolumeProfileResult:
    distribution: VolumeDistribution
    quality: MinuteQuality
    source: str
    source_version: str
    data_version: str
    adjustment_version: str
    adjustment_source: str
