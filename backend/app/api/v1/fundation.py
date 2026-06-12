from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth

router = APIRouter(prefix="/fundation", tags=["fundation"])


class SectorsRequest(BaseModel):
    type: int  #1：行业，2：概念，3：全部
@router.post("/realtime-sectors")
async def get_realtime_sectors(body: SectorsRequest, _auth=Depends(verify_auth)):
    """获取板块的实时行情"""
    # try:
    #     data = await svc.get_realtime_sectors(body.type)
    #     return ApiResponse.ok(data)
    # except Exception as e:
    #     return ApiResponse.error(500, str(e))
    pass


@router.post("/sw-industry")
async def get_sw_industry(_auth=Depends(verify_auth)):
    """获取申万的行业分类"""

    # 返回一二三级，都返回
    pass







