"""上证指数及沪深300指数日 K 线接口。"""

import math
from typing import Any, Literal

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field

from app.api.response import ResponseCode, error_response, success_response
from app.data.tdx import get_index_daily_kline as fetch_index_daily_kline

router = APIRouter(tags=["market-index"])


class IndexKlineRequest(BaseModel):
    code: Literal["000001.SH", "000300.SH"] = Field(
        default="000001.SH",
        description="指数代码：000001.SH 上证指数，000300.SH 沪深300",
    )


def _number(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if math.isfinite(number) else 0.0


@router.post("/market/index/hist")
def get_index_daily_kline(request: IndexKlineRequest = Body(default=IndexKlineRequest())) -> Any:
    try:
        frame = fetch_index_daily_kline(request.code.split(".")[0])
    except Exception as exc:
        return error_response(ResponseCode.BAD_GATEWAY, str(exc))

    if frame is None or frame.empty:
        return success_response([])

    if "datetime" not in frame.columns:
        return error_response(
            ResponseCode.BAD_GATEWAY,
            "TDX response is missing datetime",
        )

    # mootdx 同时将 datetime 用作索引名和列名，先移除索引避免排序歧义。
    rows = (
        frame.reset_index(drop=True)
        .sort_values("datetime", kind="stable")
        .to_dict(orient="records")
    )
    bars: list[dict[str, Any]] = []
    previous_close: float | None = None

    for row in rows:
        close = _number(row.get("close"))
        change_pct = (
            round((close - previous_close) / previous_close * 100, 2)
            if previous_close
            else 0.0
        )
        raw_date = row.get("datetime")
        bars.append(
            {
                "trade_date": str(raw_date)[:10],
                "open": _number(row.get("open")),
                "high": _number(row.get("high")),
                "low": _number(row.get("low")),
                "close": close,
                "volume": _number(row.get("vol", row.get("volume"))),
                "amount": _number(row.get("amount")),
                "change_pct": change_pct,
            }
        )
        previous_close = close

    return success_response(bars)
