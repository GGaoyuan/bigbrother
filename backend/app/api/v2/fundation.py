from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.industry import get_sw_industry, get_sw_stock_industry
from app.service.sector import get_realtime_sectors

router = APIRouter(prefix="/fundation", tags=["v2-fundation"])


class SectorsRequest(BaseModel):
    type: int = 3  # 1：行业，2：概念，3：全部


@router.post("/realtime-sectors")
async def get_realtime_sectors_api(body: SectorsRequest, _auth=Depends(verify_auth)):
    """获取板块实时行情（桌面端）"""
    try:
        data = await get_realtime_sectors(body.type)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/sw-industry")
async def get_sw_industry_api(_auth=Depends(verify_auth)):
    """获取申万一/二/三级行业分类（桌面端）"""
    try:
        data = await get_sw_industry()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/sw-stock-industry")
async def get_sw_stock_industry_api(_auth=Depends(verify_auth)):
    """获取全市场股票申万行业归属（桌面端）"""
    try:
        data = await get_sw_stock_industry()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
