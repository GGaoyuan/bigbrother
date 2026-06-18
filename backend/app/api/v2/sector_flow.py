from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.sector_flow import (
    get_sector_flow_ranking,
    get_sector_flow_trend,
)

router = APIRouter(prefix="/sector-flow", tags=["v2-sector-flow"])


class SectorFlowTrendRequest(BaseModel):
    sector_name: str  # 板块名称，如 "电源设备"


@router.post("/ranking")
async def get_sector_flow_ranking_api(_auth=Depends(verify_auth)):
    """今日板块资金流入/流出排行 + 全量列表（DAILY 缓存）。"""
    try:
        data = await get_sector_flow_ranking()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/trend")
async def get_sector_flow_trend_api(
    body: SectorFlowTrendRequest, _auth=Depends(verify_auth)
):
    """单个板块资金流历史走势，用于图表叠加（按板块 DAILY 缓存）。"""
    try:
        data = await get_sector_flow_trend(body.sector_name)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
