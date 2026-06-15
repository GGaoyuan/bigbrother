from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service import capital as capital_svc

router = APIRouter(prefix="/capital", tags=["capital"])


class DragonTigerRequest(BaseModel):
    start_date: str | None = None
    end_date: str | None = None


@router.post("/northbound")
async def get_northbound(_auth=Depends(verify_auth)):
    """北向资金实时 + 历史"""
    try:
        data = await capital_svc.get_northbound_data()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/margin")
async def get_margin(_auth=Depends(verify_auth)):
    """两融余额（沪/深）"""
    try:
        data = await capital_svc.get_margin_data()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/dragon-tiger")
async def get_dragon_tiger(body: DragonTigerRequest, _auth=Depends(verify_auth)):
    """龙虎榜"""
    try:
        data = await capital_svc.get_dragon_tiger(body.start_date, body.end_date)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/market-flow")
async def get_market_flow(_auth=Depends(verify_auth)):
    """大盘资金流向"""
    try:
        data = await capital_svc.get_market_capital_flow()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
