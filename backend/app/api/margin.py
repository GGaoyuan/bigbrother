"""沪深两市每日融资融券汇总与同日合计。"""

from datetime import date as Date
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field

from app.api.response import ResponseCode, error_response, success_response
from app.data.margin import get_sse_margin, get_szse_margin

router = APIRouter(tags=["capital"])


class MarginRequest(BaseModel):
    date: Date | None = Field(
        default=None,
        description="交易日期 YYYY-MM-DD；不传时返回最近 60 个自然日内两市均已披露的最新交易日",
    )


METRICS = {
    "financing_balance": ("融资余额", "融资余额"),
    "financing_buy_amount": ("融资买入额", "融资买入额"),
    "securities_lending_balance": ("融券余量金额", "融券余额"),
    "securities_sold_volume": ("融券卖出量", "融券卖出量"),
    "securities_lending_volume": ("融券余量", "融券余量"),
    "margin_financing_balance": ("融资融券余额", "融资融券余额"),
}


def _value(value: Any, scale: int = 1) -> int | float:
    try:
        number = Decimal(str(value).replace(",", "")) * scale
    except InvalidOperation as exc:
        raise ValueError("融资融券数据含缺失或无效数值") from exc
    if not number.is_finite():
        raise ValueError("融资融券数据含非有限数值")
    return int(number) if number == number.to_integral_value() else float(number)


def _szse_values(frame: Any) -> dict[str, Any]:
    if len(frame) != 1:
        raise ValueError("深市融资融券汇总应为一行")
    row = frame.iloc[0]
    # 已核验固定版本 AKShare 的返回单位为亿元、亿股/亿份，保留两位小数。
    values = {name: _value(row[fields[1]], 100000000) for name, fields in METRICS.items()}
    values.update(source="SZSE", library="akshare", amount_precision=1000000, volume_precision=1000000)
    return values


@router.post("/capital/margin")
def get_margin_summary(request: MarginRequest = Body(default=MarginRequest())) -> Any:
    end_date = request.date or datetime.now(ZoneInfo("Asia/Shanghai")).date()
    try:
        frame = get_sse_margin(end_date)
        rows = {
            Date.fromisoformat(str(row["信用交易日期"])): row
            for row in frame.to_dict(orient="records")
        }
        start_date = end_date - timedelta(days=59)
        candidates = sorted((day for day in rows if start_date <= day <= end_date), reverse=True)
        if request.date:
            candidates = [request.date] if request.date in rows else []
        for day in candidates:
            report = get_szse_margin(day)
            if report.empty:
                continue
            sse = {name: _value(rows[day][fields[0]]) for name, fields in METRICS.items()}
            sse.update(source="SSE", library="akshare", amount_precision=1, volume_precision=1,
                       financing_repayment_estimated=True, financing_repayment_amount=None)
            szse = _szse_values(report)
            szse["financing_repayment_amount"] = None
            szse["financing_repayment_estimated"] = True
            earlier = sorted((previous for previous in rows if previous < day), reverse=True)
            if earlier:
                previous_sse = rows[earlier[0]]
                sse["financing_repayment_amount"] = (
                    _value(previous_sse["融资余额"]) + sse["financing_buy_amount"]
                    - sse["financing_balance"]
                )
                previous_report = get_szse_margin(earlier[0])
                if not previous_report.empty:
                    previous = _szse_values(previous_report)
                    # 库的两市汇总均无偿还额字段，按余额关系由前一交易日推算。
                    szse["financing_repayment_amount"] = (
                        previous["financing_balance"] + szse["financing_buy_amount"]
                        - szse["financing_balance"]
                    )
            total = {name: sse[name] + szse[name] for name in METRICS}
            total["financing_repayment_amount"] = (
                sse["financing_repayment_amount"] + szse["financing_repayment_amount"]
                if sse["financing_repayment_amount"] is not None
                and szse["financing_repayment_amount"] is not None else None
            )
            total.update(financing_repayment_estimated=True, amount_precision=1000000,
                         volume_precision=1000000)
            return success_response([{
                "trade_date": day.isoformat(),
                "units": {"amount": "CNY", "volume": "股/份"},
                "sse": sse,
                "szse": szse,
                "total": total,
            }])
        return success_response([])
    except Exception as exc:
        return error_response(ResponseCode.BAD_GATEWAY, str(exc))
