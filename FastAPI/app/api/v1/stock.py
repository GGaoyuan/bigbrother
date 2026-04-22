from typing import Optional
from fastapi import APIRouter
from app.schemas.stock import ProviderEnum
from app.services.stock_service import StockService

router = APIRouter(prefix="/stock", tags=["stock"])
service = StockService()


@router.get("/daily/{code}")
async def get_daily(
    code: str,
    start_date: str,
    end_date: str,
    provider: Optional[ProviderEnum] = ProviderEnum.BAOSTOCK,
):
    return await service.get_daily(code, start_date, end_date, provider.value if provider else None)


@router.get("/realtime/{code}")
async def get_realtime(
    code: str,
    provider: Optional[ProviderEnum] = ProviderEnum.BAOSTOCK,
):
    return await service.get_realtime(code, provider.value if provider else None)
