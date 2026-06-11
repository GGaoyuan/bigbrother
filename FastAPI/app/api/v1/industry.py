from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth

router = APIRouter(prefix="/industry", tags=["industry"])


class SwIndustry(BaseModel):
    level: int
@router.post("/sw-industry")
async def get_sw_industry(body: SwIndustry, _auth=Depends(verify_auth)):
    """获取申万的行业分类"""
    # try:
    #     data = await svc.get_realtime_sectors(body.type)
    #     return ApiResponse.ok(data)
    # except Exception as e:
    #     return ApiResponse.error(500, str(e))
    pass