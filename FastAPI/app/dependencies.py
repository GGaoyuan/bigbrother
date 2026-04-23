from fastapi import Header, HTTPException
from typing import Optional
from app.core.response import ApiResponse


async def verify_auth(
    token: Optional[str] = Header(default=None),
    uid: Optional[str] = Header(default=None),
):
    if not token or not uid:
        raise HTTPException(
            status_code=200,
            detail=ApiResponse.error(502, "用户未登录").model_dump(),
        )
    return {"token": token, "uid": uid}
