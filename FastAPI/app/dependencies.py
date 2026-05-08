from fastapi import Header, HTTPException
from typing import Optional
from app.core.response import ApiResponse


async def verify_auth(
    token: Optional[str] = Header(default=None),
    uid: Optional[str] = Header(default=None),
):
    # 暂时注释，以后用
    # if not token or not uid:
    #     raise HTTPException(
    #         status_code=200,
    #         detail=ApiResponse.error(502, "用户未登录").model_dump(),
    #     )
    token = 'token1111'
    uid = 'uid222222'
    return {"token": token, "uid": uid}
