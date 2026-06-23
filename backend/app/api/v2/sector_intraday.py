from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.sector_intraday import get_sector_intraday_ranking

router = APIRouter(prefix="/sector-intraday")


class IntradayRankingRequest(BaseModel):
    top_n: int = Field(default=12, ge=1, le=30, description="流入 top N")
    bottom_n: int = Field(default=12, ge=1, le=30, description="流出 bottom N")


@router.post("/ranking")
async def ranking(req: IntradayRankingRequest, _auth=Depends(verify_auth)):
    """板块日内资金流向排行 + 头尾走势曲线（盘中 1h 缓存）"""
    data = await get_sector_intraday_ranking(req.top_n, req.bottom_n)
    return ApiResponse.ok(data)
