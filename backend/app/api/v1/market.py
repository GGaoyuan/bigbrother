from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service import index_analysis as index_svc

router = APIRouter(prefix="/market", tags=["market"])


class IndexHistRequest(BaseModel):
    symbol: str = "000001"
    index_name: str = ""
    start_date: str | None = None
    end_date: str | None = None


@router.post("/index/core")
async def get_core_index(_auth=Depends(verify_auth)):
    """三大指数日K + 均线/支撑压力/趋势"""
    try:
        data = await index_svc.get_core_index_analysis()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/index/spot")
async def get_index_spot(_auth=Depends(verify_auth)):
    """实时指数行情"""
    try:
        data = await index_svc.get_index_spot()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/index/style")
async def get_style_compare(_auth=Depends(verify_auth)):
    """大小盘风格对比"""
    try:
        data = await index_svc.get_style_compare()
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/index/hist")
async def get_index_hist(body: IndexHistRequest, _auth=Depends(verify_auth)):
    """单指数历史日K"""
    try:
        from app.providers.index_data import get_index_daily_hist
        from app.service.bean import tag_datasource
        from app.base.datasource_from import DatasourceFrom
        from app.service.indicators import enrich_index_indicators

        bars = await get_index_daily_hist(
            body.symbol, body.index_name, body.start_date, body.end_date
        )
        rows = enrich_index_indicators(
            tag_datasource(bars, DatasourceFrom.EAST_MONEY)
        )
        return ApiResponse.ok(rows)
    except Exception as e:
        return ApiResponse.error(500, str(e))
