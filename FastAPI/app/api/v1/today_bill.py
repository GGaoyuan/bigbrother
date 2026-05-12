import asyncio
import efinance as ef
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.core.response import ApiResponse
from app.dependencies import verify_auth
from app.bean import TodayBillBean

router = APIRouter()


def _safe_float(val) -> float:
    try:
        v = float(val) if val is not None else 0.0
        return 0.0 if (v != v) else v
    except (ValueError, TypeError):
        return 0.0


async def _fetch_bill(code: str) -> List[TodayBillBean]:
    df = await asyncio.to_thread(ef.stock.get_today_bill, code)
    if df is None or df.empty:
        return []
    result = []
    for _, row in df.iterrows():
        result.append(TodayBillBean(
            time=str(row.get("时间", "")),
            main_net_inflow=_safe_float(row.get("主力净流入")),
            small_net_inflow=_safe_float(row.get("小单净流入")),
            medium_net_inflow=_safe_float(row.get("中单净流入")),
            large_net_inflow=_safe_float(row.get("大单净流入")),
            super_large_net_inflow=_safe_float(row.get("超大单净流入")),
        ))
    return result


class TodayBillRequest(BaseModel):
    codes: List[str]  # 股票代码列表


@router.post("/stock/today-bill")
async def get_today_bill(body: TodayBillRequest, _auth=Depends(verify_auth)):
    """获取多只股票日内分钟级单子流入流出数据，并发请求"""
    try:
        tasks = [_fetch_bill(code) for code in body.codes]
        results = await asyncio.gather(*tasks)
        data = {code: bills for code, bills in zip(body.codes, results)}
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


class RealtimeQuotesRequest(BaseModel):
    codes: List[str]  # 股票代码列表


@router.post("/stock/realtime-quotes")
async def get_realtime_quotes(body: RealtimeQuotesRequest, _auth=Depends(verify_auth)):
    """获取多只股票实时行情"""
    try:
        df = await asyncio.to_thread(ef.stock.get_realtime_quotes)
        if df is None or df.empty:
            return ApiResponse.ok({})
        df = df[df["股票代码"].isin(body.codes)]
        return ApiResponse.ok(df.to_dict(orient="records"))
    except Exception as e:
        return ApiResponse.error(500, str(e))
