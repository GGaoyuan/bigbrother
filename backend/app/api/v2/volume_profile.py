from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.volume_kline import VolumeKlineService

router = APIRouter(prefix="/volume-profile", tags=["v2-volume-profile"])


class VolumeKlineRequest(BaseModel):
    symbol: str = Field(description="6 位证券代码，如 600519")
    period: str = Field(default="day", description="周期：1m / 5m / 30m / day")
    count: int = Field(default=300, ge=20, le=2000, description="返回最近多少根 K 线")


@router.post("/kline")
async def volume_kline(body: VolumeKlineRequest, _auth=Depends(verify_auth)):
    """成交量分布 K 线（easy_tdx，含成交量，不缓存）。"""
    try:
        result = await VolumeKlineService(body.symbol, body.period, body.count).execute()
        if not result.success:
            return ApiResponse.error(500, result.error or "volume kline failed")
        return ApiResponse.ok(result.data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
