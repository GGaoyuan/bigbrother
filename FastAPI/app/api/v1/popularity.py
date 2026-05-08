import asyncio
import efinance as ef
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.response import ApiResponse
from app.dependencies import verify_auth

router = APIRouter()


async def _fetch(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)


def _to_ef_date(yyyymmdd: str) -> str:
    """YYYYMMDD -> YYYY-MM-DD"""
    return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}"


def _safe_float(val) -> float:
    try:
        v = float(val) if val is not None else 0.0
        return 0.0 if (v != v) else v  # nan check
    except (ValueError, TypeError):
        return 0.0


# ── 龙虎榜统计 ───────────────────────────────────────────────────────────────

class TopListRecord(BaseModel):
    code: str
    name: str
    date: str
    interpretation: str
    close: float
    change_pct: float
    turnover_rate: float
    net_buy: float
    buy_amount: float
    sell_amount: float
    lhb_turnover: float
    market_turnover: float
    net_buy_ratio: float
    turnover_ratio: float
    float_market_cap: float
    reason: str


class TopListGrouped(BaseModel):
    code: str
    name: str
    count: int
    records: list[TopListRecord]


@router.get("/popularity/top-list")
async def get_top_list(start_date: str, end_date: str, _auth=Depends(verify_auth)):
    """龙虎榜统计，start_date/end_date 格式 YYYYMMDD"""
    try:
        df = await _fetch(
            ef.stock.get_daily_billboard,
            start_date=_to_ef_date(start_date),
            end_date=_to_ef_date(end_date),
        )
        if df is None or df.empty:
            return ApiResponse.ok({"mode": "single" if start_date == end_date else "range", "records": [], "groups": []})

        records: list[TopListRecord] = []
        for _, row in df.iterrows():
            records.append(TopListRecord(
                code=str(row.get("股票代码", "")),
                name=str(row.get("股票名称", "")),
                date=str(row.get("上榜日期", "")),
                interpretation=str(row.get("解读", "")),
                close=_safe_float(row.get("收盘价")),
                change_pct=_safe_float(row.get("涨跌幅")),
                turnover_rate=_safe_float(row.get("换手率")),
                net_buy=_safe_float(row.get("龙虎榜净买额")),
                buy_amount=_safe_float(row.get("龙虎榜买入额")),
                sell_amount=_safe_float(row.get("龙虎榜卖出额")),
                lhb_turnover=_safe_float(row.get("龙虎榜成交额")),
                market_turnover=_safe_float(row.get("市场总成交额")),
                net_buy_ratio=_safe_float(row.get("净买额占总成交比")),
                turnover_ratio=_safe_float(row.get("成交额占总成交比")),
                float_market_cap=_safe_float(row.get("流通市值")),
                reason=str(row.get("上榜原因", "")),
            ))

        # 单日模式：直接返回列表
        if start_date == end_date:
            return ApiResponse.ok({"mode": "single", "records": records})

        # 范围模式：按股票分组，统计上榜次数
        grouped: dict[str, TopListGrouped] = {}
        for r in records:
            if r.code not in grouped:
                grouped[r.code] = TopListGrouped(code=r.code, name=r.name, count=0, records=[])
            grouped[r.code].count += 1
            grouped[r.code].records.append(r)

        result = sorted(grouped.values(), key=lambda x: x.count, reverse=True)
        return ApiResponse.ok({"mode": "range", "groups": result})
    except Exception as e:
        return ApiResponse.error(500, str(e))
