"""A-share charts and fixed-range volume estimates based on one-minute candles."""

from typing import Annotated, Literal

from fastapi import APIRouter, Body, Path, Query
from pydantic import BaseModel, ConfigDict, Field

from app.api.response import ApiResponse, error_response, success_response
from app.data.astock_data_provider import AStockDataProvider
from app.data.easy_tdx_minute_provider import EasyTdxMinuteProvider
from app.data.sina_minute_provider import SinaMinuteProvider
from app.data.stock_market import StockMarket
from app.data.stock_market_types import MarketDataError, MinuteCoverageError, UnsupportedMarketData
from app.data.tdx_stock_provider import TdxProvider


router = APIRouter(prefix="/stocks", tags=["stocks"])
tdx = TdxProvider()
astock = AStockDataProvider()
market = StockMarket(
    (tdx, astock),
    minute_providers=(tdx, SinaMinuteProvider(), EasyTdxMinuteProvider(), astock),
)
Symbol = Annotated[str, Path(pattern=r"^[0-9]{6}$", description="六位 A 股代码")]
MAX_TIMESTAMP = 4_102_444_800
TimeQuery = Annotated[int, Query(ge=0, le=MAX_TIMESTAMP, description="北京时间对应的 Unix 秒")]


class KlineRequest(BaseModel):
    interval: Literal["1d", "60m", "5m"] = "1d"
    start: int | None = Field(default=None, ge=0, le=MAX_TIMESTAMP)
    end: int | None = Field(default=None, ge=0, le=MAX_TIMESTAMP)
    adjust: Literal["qfq"] = "qfq"
    cursor: int | None = Field(default=None, ge=0, le=MAX_TIMESTAMP)
    limit: int = Field(default=320, ge=1, le=3000)


class ProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: int = Field(ge=0, le=MAX_TIMESTAMP)
    end: int = Field(ge=0, le=MAX_TIMESTAMP)


def _range(start, end):
    if start is not None and end is not None and start >= end:
        raise UnsupportedMarketData("开始时间必须早于结束时间")


def _response(call, *args):
    try:
        return success_response(call(*args))
    except MinuteCoverageError as exc:
        return error_response(exc.status_code, str(exc), {"data_quality": exc.quality})
    except MarketDataError as exc:
        return error_response(exc.status_code, str(exc))


@router.get("/{symbol}", response_model=ApiResponse, summary="股票信息")
def stock(symbol: Symbol):
    return _response(market.stock, symbol)


@router.post("/{symbol}/klines", response_model=ApiResponse, summary="历史 K 线")
def klines(symbol: Symbol, body: KlineRequest = Body(default=KlineRequest())):
    return _response(market.chart_klines, symbol, body.interval, body.start, body.end, body.limit, body.cursor)


@router.get("/{symbol}/ticks/coverage", response_model=ApiResponse, summary="逐笔数据覆盖情况")
def coverage(symbol: Symbol):
    return _response(market.coverage, symbol)


@router.get("/{symbol}/ticks", response_model=ApiResponse, summary="分页获取真实行情源的成交明细")
def ticks(
    symbol: Symbol,
    start: TimeQuery,
    end: TimeQuery,
    limit: Annotated[int, Query(ge=1, le=2000)] = 500,
    cursor: Annotated[str | None, Query(max_length=160)] = None,
):
    return _response(_ticks, symbol, start, end, limit, cursor)


def _ticks(symbol, start, end, limit, cursor):
    _range(start, end)
    return market.ticks(symbol, start, end, limit, cursor)


@router.post("/{symbol}/volume-profile", response_model=ApiResponse, summary="基于 1 分钟 K 线估算价位分布")
def volume_profile(symbol: Symbol, body: ProfileRequest):
    return _response(_profile, symbol, body)


def _profile(symbol, body):
    _range(body.start, body.end)
    return market.volume_profile(symbol, body.start, body.end)
