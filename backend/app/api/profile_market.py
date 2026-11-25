"""Mock-backed historical candles and trade data for fixed-range volume profiles."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.api.response import ApiResponse, ResponseCode, success_response
from app.console_logging import observe_provider
from app.data.profile_market_mock import STOCK_NAMES, Period, get_history, get_trades


router = APIRouter(prefix="/market/profile", tags=["market-profile"])
StockCode = Annotated[str, Query(pattern=r"^[0-9]{6}$", description="六位股票代码")]
Timestamp = Annotated[int, Query(ge=0, description="Unix 秒时间戳")]


@router.get("/history")
def get_profile_history(code: StockCode, period: Period) -> ApiResponse:
    """Return synthetic candles for the requested period and a daily overview."""
    try:
        with observe_provider("simulated", "profile_history", symbol=code, period=period):
            bars, overview = get_history(code, period)
    except Exception as exc:
        raise HTTPException(ResponseCode.BAD_GATEWAY, "模拟历史行情暂不可用") from exc

    return success_response({
        "code": code,
        "name": STOCK_NAMES.get(code, "模拟标的"),
        "source": "simulated",
        "bars": bars,
        "overview": overview,
    })


@router.get("/trades")
def get_profile_trades(code: StockCode, start: Timestamp, end: Timestamp) -> ApiResponse:
    """Return synthetic trades with inclusive start and exclusive end timestamps."""
    if start >= end:
        raise HTTPException(ResponseCode.VALIDATION_ERROR, "开始时间必须早于结束时间")

    try:
        with observe_provider("simulated", "profile_trades", symbol=code, start=start, end=end):
            trades = get_trades(code, start, end)
    except Exception as exc:
        raise HTTPException(ResponseCode.BAD_GATEWAY, "模拟逐笔成交暂不可用") from exc

    return success_response({
        "code": code,
        "source": "simulated",
        "trades": trades,
    })
