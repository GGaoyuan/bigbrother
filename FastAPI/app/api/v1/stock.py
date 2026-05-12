from fastapi import APIRouter, Depends
from app.core.response import ApiResponse
from app.dependencies import verify_auth
import app.service.fundation_service as svc

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/daily/{code}")
async def get_daily(code: str, start_date: str, end_date: str, _auth=Depends(verify_auth)):
    """获取单只股票日线数据"""
    try:
        data = await svc.get_daily(code, start_date, end_date)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.get("/realtime/{code}")
async def get_realtime(code: str, _auth=Depends(verify_auth)):
    """获取单只股票实时行情"""
    try:
        data = await svc.get_realtime_quotes([code])
        return ApiResponse.ok(data[0] if data else None)
    except Exception as e:
        return ApiResponse.error(500, str(e))
