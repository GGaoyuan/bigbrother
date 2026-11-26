"""Register individual stock endpoints under a common URL prefix."""

from fastapi import APIRouter

from . import info, klines, volume_profile


router = APIRouter(prefix="/stocks", tags=["stocks"])
router.include_router(info.router)
router.include_router(klines.router)
router.include_router(volume_profile.router)
