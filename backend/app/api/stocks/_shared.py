"""Request field constraints and service dependencies for the stock routes."""

from typing import Annotated

from fastapi import Depends, Path, Request

from app.services.klines import KlineService
from app.services.stock_info import StockInfoService
from app.services.volume_profile import VolumeProfileService


Symbol = Annotated[str, Path(pattern=r"^[0-9]{6}$", description="六位 A 股代码")]
MAX_TIMESTAMP = 4_102_444_800


def get_stock_service(request: Request) -> StockInfoService:
    return request.app.state.stocks


def get_kline_service(request: Request) -> KlineService:
    return request.app.state.klines


def get_profile_service(request: Request) -> VolumeProfileService:
    return request.app.state.profile


StockServiceDependency = Annotated[StockInfoService, Depends(get_stock_service)]
KlineServiceDependency = Annotated[KlineService, Depends(get_kline_service)]
ProfileServiceDependency = Annotated[VolumeProfileService, Depends(get_profile_service)]
