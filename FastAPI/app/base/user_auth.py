from fastapi import Header, HTTPException
from typing import Optional
from app.base.api_response import ApiResponse


async def verify_auth(
    token: Optional[str] = Header(default=None),
    uid: Optional[str] = Header(default=None),
):
    if not token or not uid:
        raise HTTPException(
            status_code=200,
            detail=ApiResponse.error(502, "用户未登录").model_dump(),
        )
    # beta
    if token != 'gaoyuanzuishuai' or uid != '1993':
        raise HTTPException(
            status_code=200,
            detail=ApiResponse.error(502, "你不是源大").model_dump(),
        )
    else:
        return {"token": token, "uid": uid}

# 最好写config中去
whiteList = [

]