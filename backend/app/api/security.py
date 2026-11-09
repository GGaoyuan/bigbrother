"""Mock token validation for protected API routes."""

from fastapi import Header, HTTPException

from app.api.response import ResponseCode

MOCK_USER_TOKEN = "mock-token-10001"


def require_user_token(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> str:
    if not authorization or not authorization.strip():
        raise HTTPException(
            status_code=ResponseCode.UNAUTHORIZED,
            detail="未登录",
        )

    authorization = authorization.strip()
    scheme, separator, token = authorization.partition(" ")

    if not separator and authorization.strip().lower() == "bearer":
        raise HTTPException(
            status_code=ResponseCode.UNAUTHORIZED,
            detail="未登录",
        )

    if separator and not token.strip():
        raise HTTPException(
            status_code=ResponseCode.UNAUTHORIZED,
            detail="未登录",
        )

    if scheme.lower() != "bearer" or token.strip() != MOCK_USER_TOKEN:
        raise HTTPException(
            status_code=ResponseCode.UNAUTHORIZED,
            detail="token错误",
        )

    return token.strip()
