from typing import Optional
from fastapi import APIRouter, Depends
from app.schemas.stock import ProviderEnum
from app.schemas.response import ApiResponse
from app.providers.akshare import AKShareProvider
from app.dependencies import verify_auth
from app.core.config import settings

router = APIRouter(prefix="/stock", tags=["stock"])

_providers = {
    "akshare": AKShareProvider(),
}


@router.get("/daily/{code}")
async def get_daily(
    code: str,
    start_date: str,
    end_date: str,
    provider: Optional[ProviderEnum] = ProviderEnum.BAOSTOCK,
    _auth=Depends(verify_auth),
):
    provider_name = provider.value if provider else settings.datasource
    provider_instance = _providers[provider_name]
    data = await provider_instance.get_daily(code, start_date, end_date)
    return ApiResponse.ok(data)


@router.get("/realtime/{code}")
async def get_realtime(
    code: str,
    provider: Optional[ProviderEnum] = ProviderEnum.BAOSTOCK,
    _auth=Depends(verify_auth),
):
    provider_name = provider.value if provider else settings.datasource
    provider_instance = _providers[provider_name]
    data = await provider_instance.get_realtime(code)
    return ApiResponse.ok(data)
