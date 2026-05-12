from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.core.response import ApiResponse
from app.dependencies import verify_auth
import app.service.fundation_service as svc

router = APIRouter(prefix="/fundation", tags=["fundation"])


class CodesRequest(BaseModel):
    codes: List[str]  # 股票代码列表


class DailyRequest(BaseModel):
    code: str        # 股票代码
    start: str       # 开始日期，格式 YYYYMMDD
    end: str         # 结束日期，格式 YYYYMMDD


@router.post("/today-bill")
async def get_today_bill(body: CodesRequest, _auth=Depends(verify_auth)):
    """获取多只股票日内分钟级单子流入流出数据，并发请求"""
    try:
        data = await svc.get_today_bill(body.codes)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/realtime-quotes")
async def get_realtime_quotes(body: CodesRequest, _auth=Depends(verify_auth)):
    """获取多只股票实时行情"""
    try:
        data = await svc.get_realtime_quotes(body.codes)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/daily")
async def get_daily(body: DailyRequest, _auth=Depends(verify_auth)):
    """获取单只股票日线数据"""
    try:
        data = await svc.get_daily(body.code, body.start, body.end)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/market-sentiment")
async def get_market_sentiment(_auth=Depends(verify_auth)):
    """获取全市场情绪数据"""
    try:
        data = await svc.get_market_sentiment()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
