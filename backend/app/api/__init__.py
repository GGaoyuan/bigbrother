"""在统一的 URL 前缀下注册各个股票接口。"""

from fastapi import APIRouter

from . import kline, stock, volume_profile


router = APIRouter(prefix="/stocks", tags=["stocks"])
router.include_router(stock.router)
router.include_router(kline.router)
router.include_router(volume_profile.router)
