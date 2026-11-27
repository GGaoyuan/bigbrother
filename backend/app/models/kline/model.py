"""定义 K 线字段和行情结果。"""

from dataclasses import dataclass, field
from typing import Literal


ChartInterval = Literal["1d", "60m", "5m"]
Interval = Literal[ChartInterval, "1m"]
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
    adjustment_version: str
