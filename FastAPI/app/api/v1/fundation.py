from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.base.api_response import ApiResponse
from app.general.dependencies import verify_auth
import app.service.fundation_service as svc

router = APIRouter(prefix="/fundation", tags=["fundation"])


class SectorsRequest(BaseModel):
    type: int  #1：行业，2：概念，3：全部
@router.post("/realtime-sectors")
async def get_realtime_sectors(body: SectorsRequest, _auth=Depends(verify_auth)):
    """获取板块的实时行情"""
    try:
        data = await svc.get_realtime_sectors(body.type)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))

