import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.market_index import router as market_index_router
from app.api.margin import router as margin_router
from app.api.profile_market import router as profile_market_router
from app.api.response import ResponseCode, error_response
from app.api.stocks import router as stocks_router
from app.console_logging import log_event
from app.middleware.request_logging import RequestLoggingMiddleware

logger = logging.getLogger(__name__)

class LoggedFastAPI(FastAPI):
    def build_middleware_stack(self):
        return RequestLoggingMiddleware(super().build_middleware_stack())


app = LoggedFastAPI(title="BigBrother API", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return error_response(
        code=ResponseCode.VALIDATION_ERROR,
        message="请求参数校验失败",
        status_code=422,
    )


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "请求失败"
    return error_response(
        code=exc.status_code,
        message=message,
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
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

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(?:localhost|127\.0\.0\.1)(?::\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market_index_router, prefix="/api/v1")
app.include_router(margin_router, prefix="/api/v1")
app.include_router(profile_market_router, prefix="/api/v1")
app.include_router(stocks_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
