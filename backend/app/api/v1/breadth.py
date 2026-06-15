from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service import market_breadth as breadth_svc

router = APIRouter(prefix="/breadth", tags=["breadth"])


class FundFlowRankRequest(BaseModel):
    indicator: str = "今日"


class LimitPoolRequest(BaseModel):
    date: str | None = None


@router.post("/volume")
async def get_volume_summary(_auth=Depends(verify_auth)):
    """两市成交与市场总貌"""
    try:
        data = await breadth_svc.get_market_volume_summary()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/limit-pools")
async def get_limit_pools(body: LimitPoolRequest, _auth=Depends(verify_auth)):
    """涨跌停/炸板/强势股池"""
    try:
        data = await breadth_svc.get_limit_pool_summary(body.date)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/fund-flow-rank")
async def get_fund_flow_rank(body: FundFlowRankRequest, _auth=Depends(verify_auth)):
    """全市场个股资金流排名"""
    try:
        data = await breadth_svc.get_fund_flow_rank(body.indicator)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
