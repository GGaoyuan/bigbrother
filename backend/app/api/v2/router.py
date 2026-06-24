from fastapi import APIRouter

from app.api.v2.fundation import router as fundation_router
from app.api.v2.hotlist import router as hotlist_router
from app.api.v2.market_cap import router as market_cap_router
from app.api.v2.sector_flow import router as sector_flow_router
from app.api.v2.sector_intraday import router as sector_intraday_router
from app.api.v2.tdx import router as tdx_router

router = APIRouter(tags=["v2-desktop"])

router.include_router(fundation_router)
router.include_router(hotlist_router)
router.include_router(market_cap_router)
router.include_router(sector_flow_router)
router.include_router(sector_intraday_router)
router.include_router(tdx_router)
