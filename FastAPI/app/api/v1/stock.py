from typing import Optional
from fastapi import APIRouter, Depends
from app.bean import ProviderEnum
from app.core.response import ApiResponse
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
    provider: Optional[ProviderEnum] = None,
    _auth=Depends(verify_auth),
):
    provider_name = provider.value if provider else settings.datasource
    data = await _providers[provider_name].get_daily(code, start_date, end_date)
    return ApiResponse.ok(data)


@router.get("/realtime/{code}")
async def get_realtime(
    code: str,
    provider: Optional[ProviderEnum] = None,
    _auth=Depends(verify_auth),
):
    provider_name = provider.value if provider else settings.datasource
    data = await _providers[provider_name].get_realtime(code)
    return ApiResponse.ok(data)
