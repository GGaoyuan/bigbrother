"""Shanghai Composite K-line API."""

import math
from typing import Any

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.data.tdx import get_shanghai_index_daily_kline

router = APIRouter(tags=["market-index"])


class IndexKlineRequest(BaseModel):
    limit: int = Field(default=500, ge=1, le=800)


def _number(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if math.isfinite(number) else 0.0


@router.post("/market/index/hist")
def get_index_daily_kline(
    request: IndexKlineRequest = Body(default=IndexKlineRequest()),
) -> Any:
    try:
        frame = get_shanghai_index_daily_kline(request.limit)
    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={"code": 502, "message": str(exc), "data": None},
        )

    if frame is None or frame.empty:
        return {"code": 200, "message": "success", "data": []}

    if "datetime" not in frame.columns:
        return JSONResponse(
            status_code=502,
            content={
                "code": 502,
                "message": "TDX response is missing datetime",
                "data": None,
            },
        )

    rows = frame.sort_values("datetime", kind="stable").to_dict(orient="records")
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

    return {"code": 200, "message": "success", "data": bars}
