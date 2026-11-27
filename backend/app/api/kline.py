"""查询股票的前复权 K 线。"""

from typing import Literal

from fastapi import APIRouter, Body
from pydantic import BaseModel, ConfigDict, Field

from app.core.response import ApiResponse, success_response
from app.models.model import ChartInterval

from ._shared import KlineServiceDependency, MAX_TIMESTAMP, Symbol


router = APIRouter()


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


@router.post("/{symbol}/klines", response_model=ApiResponse[KlineResponse], summary="历史 K 线")
def klines(
    symbol: Symbol, service: KlineServiceDependency, body: KlineRequest = Body(default=KlineRequest()),
) -> ApiResponse[KlineResponse]:
    result = service.get_chart(symbol, body.interval, body.start, body.end, body.limit, body.cursor)
    return success_response(KlineResponse(
        symbol=symbol,
        interval=body.interval,
        source=result.history.source,
        source_version=result.history.source_version,
        adjustment_version=result.adjustment_version,
        adjustment_source=result.adjustment_source,
        bars=tuple(CandleResponse.model_validate(bar) for bar in result.history.bars),
        next_cursor=result.next_cursor,
    ))
