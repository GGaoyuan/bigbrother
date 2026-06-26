from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.index_kline import IndexKlineService, list_supported_indices

router = APIRouter(prefix="/index", tags=["v2-index"])


class IndexKlineRequest(BaseModel):
    symbol: str = Field(description="指数代码，如 H30269 / HSHYLV")
    period: str = Field(default="day", description="周期：day / week / month")
    limit: int = Field(default=500, ge=10, le=5000, description="返回最近多少根 K 线")


@router.post("/list")
async def index_list(_auth=Depends(verify_auth)):
    """可选指数列表（红利低波 / 恒生港股通高股息低波动）。"""
    try:
        return ApiResponse.ok(list_supported_indices())
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/kline")
async def index_kline(body: IndexKlineRequest, _auth=Depends(verify_auth)):
    """指数 K 线（日/周/月，实时获取，不缓存）。"""
    try:
        result = await IndexKlineService(body.symbol, body.period, body.limit).execute()
        if not result.success:
            return ApiResponse.error(500, result.error or "index kline failed")
        return ApiResponse.ok(result.data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
