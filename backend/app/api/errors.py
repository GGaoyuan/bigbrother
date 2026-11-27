"""将业务和框架异常转换为统一的 HTTP 响应格式。"""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from app.core.exceptions import MarketDataError, StockNotFound, UnsupportedMarketData
from app.core.logger import log_event
from app.core.response import ResponseCode, error_response

from .volume_profile import MinuteCoverageError


logger = logging.getLogger(__name__)


async def handle_market_error(request: Request, exc: MarketDataError) -> JSONResponse:
    if isinstance(exc, MinuteCoverageError):
        return error_response(409, str(exc), {"data_quality": exc.quality})
    if isinstance(exc, StockNotFound):
        return error_response(404, str(exc))
    if isinstance(exc, UnsupportedMarketData):
        return error_response(422, str(exc))
    return error_response(502, str(exc))


async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return error_response(
        code=ResponseCode.VALIDATION_ERROR,
        message="请求参数校验失败",
        status_code=422,
    )


async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "请求失败"
    return error_response(
        code=exc.status_code,
        message=message,
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    log_event("http.exception", errorType=type(exc).__name__, reason=str(exc))
    logger.error(
        "Unhandled API exception",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return error_response(
        code=ResponseCode.SERVER_ERROR,
        message="服务器内部错误",
        status_code=500,
    )


exception_handlers = {
    MarketDataError: handle_market_error,
    RequestValidationError: handle_validation_error,
    HTTPException: handle_http_error,
    Exception: handle_unexpected_error,
}
