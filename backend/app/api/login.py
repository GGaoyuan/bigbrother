"""Authentication API with temporary mock responses."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.response import ApiResponse, success_response
from app.api.security import MOCK_USER_TOKEN

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    phone: str = Field(min_length=1)
    password: str = Field(min_length=1)


@router.post("/auth/login")
def login(request: LoginRequest) -> ApiResponse:
    return success_response(
        {
            "password": None,
            "phone": request.phone,
            "nickName": "示例用户",
            "mail": None,
            "userId": "10001",
            "token": MOCK_USER_TOKEN,
        }
    )
