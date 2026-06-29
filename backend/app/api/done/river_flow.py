from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth

router = APIRouter(prefix="/river_flow", tags=["v2-river_flow"])


class IndustryTrendRequest(BaseModel):
    symbol: str  # 申万指数代码，如 "801010" 或 "801010.SI"


@router.post("/total")
async def get_total_market_cap_api(_auth=Depends(verify_auth)):
    """A股"""
    try:
        data = await get_total_market_cap_trend()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))