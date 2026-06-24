from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.hotlist import LimitPoolsService, FundFlowRankingService

router = APIRouter(prefix="/hotlist", tags=["v2-hotlist"])


class FundFlowRankingRequest(BaseModel):
    indicator: str = Field(default="今日", description="时间周期：今日/3日/5日/10日")
    limit: int = Field(default=100, ge=1, le=500, description="返回数量上限")


@router.post("/limit-pools")
async def get_limit_pools_api(_auth=Depends(verify_auth)):
    """涨停池 + 跌停池（1小时缓存）

    返回:
        {
            "limit_up": [涨停股票列表],
            "limit_down": [跌停股票列表]
        }
    """
    try:
        service = LimitPoolsService()
        result = await service.execute()
        if result.success:
            return ApiResponse.ok(result.data)
        else:
            return ApiResponse.error(500, result.error)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/fund-flow-ranking")
async def get_fund_flow_ranking_api(
    body: FundFlowRankingRequest, _auth=Depends(verify_auth)
):
    """个股主力资金流排行（1小时缓存）

    参数:
        indicator: 今日/3日/5日/10日
        limit: 返回数量上限

    返回:
        {
            "inflow": [流入股票列表],
            "outflow": [流出股票列表]
        }

    注意: 东财接口不稳定，失败时返回空列表（降级）
    """
    try:
        service = FundFlowRankingService(body.indicator, body.limit)
        result = await service.execute()
        if result.success:
            return ApiResponse.ok(result.data)
        else:
            # 降级：失败时返回空
            return ApiResponse.ok({"inflow": [], "outflow": []})
    except Exception as e:
        return ApiResponse.error(500, str(e))
