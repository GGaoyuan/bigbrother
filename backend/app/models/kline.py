from dataclasses import dataclass, field
from math import isfinite
from typing import Literal


Interval = Literal["day", "week", "month", "1m", "5m", "60m"]
ChartInterval = Literal["1d", "60m", "5m"]
Adjustment = Literal["none", "qfq", "hfq"]
VolumeUnit = Literal["shares", "lots", "rounded_lots", "unknown"]


@dataclass(frozen=True, slots=True)
class Candle:
    """Half-open Unix seconds in the Shanghai session, CNY prices and share volume.

    Prices are unadjusted unless marked otherwise. Amount is in CNY and can be
    absent when the source lacks a reliable value. Original volume may be
    absent and its unit may be unknown. Precision is the published share
    increment, independent of the input unit.
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

    def has_valid_ohlcv(self) -> bool:
        return (
            all(isfinite(price) for price in (self.open, self.high, self.low, self.close))
            and 0 < self.low <= min(self.open, self.close) <= max(self.open, self.close) <= self.high
            and type(self.volume) is int and self.volume >= 0
            and (self.amount is None or (isfinite(self.amount) and self.amount >= 0))
        )


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
