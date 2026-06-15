from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service import sector as sector_svc
from app.service.industry import get_sw_industry, get_sw_stock_industry

router = APIRouter(prefix="/sector", tags=["sector"])


class SectorsRequest(BaseModel):
    type: int = 3  # 1:行业 2:概念 3:全部


class SectorFundFlowRequest(BaseModel):
    indicator: str = "今日"
    sector_type: str = "行业资金流"


@router.post("/realtime")
async def get_realtime_sectors(body: SectorsRequest, _auth=Depends(verify_auth)):
    """东财概念/行业板块实时行情"""
    try:
        data = await sector_svc.get_realtime_sectors(body.type)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/fund-flow")
async def get_sector_fund_flow(body: SectorFundFlowRequest, _auth=Depends(verify_auth)):
    """板块资金流向"""
    try:
        data = await sector_svc.get_sector_fund_flow(body.indicator, body.sector_type)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/ths-fund-flow")
async def get_ths_sector_fund_flow(_auth=Depends(verify_auth)):
    """同花顺行业/概念资金流"""
    try:
        data = await sector_svc.get_ths_sector_fund_flow()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/sw-industry")
async def get_sw_industry_api(_auth=Depends(verify_auth)):
    """申万一/二/三级行业"""
    try:
        data = await get_sw_industry()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/sw-stock-industry")
async def get_sw_stock_industry_api(_auth=Depends(verify_auth)):
    """全市场股票申万行业归属"""
    try:
        data = await get_sw_stock_industry()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
