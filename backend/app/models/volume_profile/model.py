"""定义成交量分布及其数据质量字段。"""

from dataclasses import dataclass
from typing import Literal, TypedDict


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
