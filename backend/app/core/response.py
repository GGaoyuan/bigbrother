"""封装统一的 API 响应格式。"""

from enum import IntEnum
from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ResponseCode(IntEnum):
    SUCCESS = 200
    VALIDATION_ERROR = 422
    SERVER_ERROR = 500


Data = TypeVar("Data")


class ApiResponse(BaseModel, Generic[Data]):
    code: int
    message: str
    data: Data


def success_response(data: Data, message: str = "success") -> ApiResponse[Data]:
    return ApiResponse(
        code=ResponseCode.SUCCESS,
        message=message,
        data=data,
    )


def error_response(
    code: ResponseCode | int,
    message: str,
    data: Any = None,
    status_code: int | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    response = ApiResponse(
        code=code,
        message=message,
        data={} if data is None else data,
    )
    return JSONResponse(
        status_code=status_code or int(code),
        content=jsonable_encoder(response),
        headers=headers,
    )
