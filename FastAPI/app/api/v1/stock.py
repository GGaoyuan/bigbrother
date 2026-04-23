from typing import Optional
from fastapi import APIRouter, Depends
from app.schemas.stock import ProviderEnum
from app.schemas.response import ApiResponse
from app.services.stock_service import StockService
from app.dependencies import verify_auth

router = APIRouter(prefix="/stock", tags=["stock"])
service = StockService()


@router.get("/daily/{code}")
async def get_daily(
    code: str,
    start_date: str,
    end_date: str,
    provider: Optional[ProviderEnum] = ProviderEnum.BAOSTOCK,
    _auth=Depends(verify_auth),
):
    data = await service.get_daily(code, start_date, end_date, provider.value if provider else None)
    return ApiResponse.ok(data)


@router.get("/realtime/{code}")
async def get_realtime(
    code: str,
    provider: Optional[ProviderEnum] = ProviderEnum.BAOSTOCK,
    _auth=Depends(verify_auth),
):
    data = await service.get_realtime(code, provider.value if provider else None)
    return ApiResponse.ok(data)
