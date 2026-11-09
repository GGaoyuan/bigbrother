"""Shared API response envelope helpers."""

from enum import IntEnum
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ResponseCode(IntEnum):
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    VALIDATION_ERROR = 422
    SERVER_ERROR = 500
    BAD_GATEWAY = 502


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any


def success_response(data: Any, message: str = "success") -> ApiResponse:
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
) -> JSONResponse:
    response = ApiResponse(
        code=code,
        message=message,
        data={} if data is None else data,
    )
    return JSONResponse(
        status_code=status_code or int(code),
        content=jsonable_encoder(response),
    )
