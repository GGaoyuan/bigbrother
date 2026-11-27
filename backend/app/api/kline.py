"""查询、校验并返回股票的前复权 K 线。"""

from math import isfinite
from typing import Literal

from fastapi import APIRouter, Body
from pydantic import BaseModel, ConfigDict, Field

from app.core.exceptions import ProviderUnavailable, UnsupportedMarketData
from app.core.logger import observe_provider
from app.core.response import ApiResponse, success_response
from app.core.symbols import stock_exchange
from app.models.kline.model import Candle, ChartInterval, KlineHistory
from app.models.kline.provider import KlineProvider

from ._shared import MAX_TIMESTAMP, Symbol


router = APIRouter()
provider = KlineProvider()


class KlineRequest(BaseModel):
    interval: ChartInterval = "1d"
    start: int | None = Field(default=None, ge=0, le=MAX_TIMESTAMP)
    end: int | None = Field(default=None, ge=0, le=MAX_TIMESTAMP)
    adjust: Literal["qfq"] = "qfq"
    cursor: int | None = Field(default=None, ge=0, le=MAX_TIMESTAMP)
    limit: int = Field(default=320, ge=1, le=3000)


class CandleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: int
    end_timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float | None
    original_volume_unit: str
    original_volume: int | float | None
    volume_precision_shares: int


class KlineResponse(BaseModel):
    symbol: str
    interval: ChartInterval
    adjust: Literal["qfq"] = "qfq"
    adjustment_version: str
    adjustment_source: str
    source: str
    source_version: str
    timezone: Literal["Asia/Shanghai"] = "Asia/Shanghai"
    volume_unit: Literal["shares"] = "shares"
    bars: tuple[CandleResponse, ...]
    next_cursor: int | None


def has_valid_ohlcv(bar: Candle) -> bool:
    return (
        all(isfinite(price) for price in (bar.open, bar.high, bar.low, bar.close))
        and 0 < bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high
        and type(bar.volume) is int and bar.volume >= 0
        and (bar.amount is None or (isfinite(bar.amount) and bar.amount >= 0))
    )


def _validate_bars(
    bars: tuple[Candle, ...], start: int | None, end: int | None, limit: int,
) -> tuple[Candle, ...]:
    by_time = {}
    for bar in bars:
        if not has_valid_ohlcv(bar) or not 0 <= bar.timestamp < bar.end_timestamp or bar.adjustment != "qfq":
            raise ProviderUnavailable("K 线包含非法时间、价格、成交量或复权口径")
        if ((start is not None and bar.end_timestamp <= start) or
                (end is not None and bar.timestamp >= end)):
            continue
        existing = by_time.get(bar.timestamp)
        if existing is not None and existing != bar:
            raise ProviderUnavailable("K 线包含冲突的重复时间")
        by_time[bar.timestamp] = bar
    ordered = tuple(by_time[key] for key in sorted(by_time)[-limit:])
    if not ordered:
        raise ProviderUnavailable("所请求区间无 K 线数据")
    if any(first.end_timestamp > second.timestamp for first, second in zip(ordered, ordered[1:])):
        raise ProviderUnavailable("K 线包含重叠时间区间")
    return ordered


def get_history(
    symbol: str, interval: ChartInterval,
    start: int | None, end: int | None, limit: int,
) -> KlineHistory:
    stock_exchange(symbol)

    source = provider
    adjustment_version = source.adjustment_version
    with observe_provider(
        source.name, "klines", symbol=symbol, version=source.version,
        interval=interval, adjust="qfq", start=start, end=end, limit=limit,
    ):
        bars = _validate_bars(
            source.get_klines(symbol, interval, "qfq", start, end, limit),
            start, end, limit,
        )
        return KlineHistory(bars, source.name, source.version, adjustment_version)


@router.post("/{symbol}/klines", response_model=ApiResponse[KlineResponse], summary="历史 K 线")
def klines(symbol: Symbol, body: KlineRequest = Body(default=KlineRequest())) -> ApiResponse[KlineResponse]:
    end = body.end
    if body.cursor is not None:
        end = body.cursor if end is None else min(end, body.cursor)
    if body.start is not None and end is not None and body.start >= end:
        raise UnsupportedMarketData("开始时间必须早于结束时间")

    history = get_history(symbol, body.interval, body.start, end, body.limit)
    oldest = history.bars[0].timestamp
    next_cursor = oldest if len(history.bars) == body.limit and (body.start is None or oldest > body.start) else None
    return success_response(KlineResponse(
        symbol=symbol,
        interval=body.interval,
        source=history.source,
        source_version=history.source_version,
        adjustment_version=history.adjustment_version,
        adjustment_source=history.source,
        bars=tuple(CandleResponse.model_validate(bar) for bar in history.bars),
        next_cursor=next_cursor,
    ))
