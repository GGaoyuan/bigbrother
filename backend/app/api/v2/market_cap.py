from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.market_cap import (
    get_industry_tree,
    get_industry_trend,
    get_total_market_cap_trend,
)

router = APIRouter(prefix="/market-cap", tags=["v2-market-cap"])


class IndustryTrendRequest(BaseModel):
    symbol: str  # 申万指数代码，如 "801010" 或 "801010.SI"


@router.post("/total")
async def get_total_market_cap_api(_auth=Depends(verify_auth)):
    """A股总市值走势（申万A指日线代理，每日缓存）。"""
    try:
        data = await get_total_market_cap_trend()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/industry-tree")
async def get_industry_tree_api(_auth=Depends(verify_auth)):
    """申万一/二/三级行业分类树（WEEKLY 缓存）。"""
    try:
        data = await get_industry_tree()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/industry-trend")
async def get_industry_trend_api(body: IndustryTrendRequest, _auth=Depends(verify_auth)):
    """单个申万行业指数走势，用于叠加到总市值图表（按行业每日缓存）。"""
    try:
        data = await get_industry_trend(body.symbol)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
