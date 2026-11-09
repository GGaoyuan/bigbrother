import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.config import router as config_router
from app.api.login import router as login_router
from app.api.market_index import router as market_index_router
from app.api.response import ResponseCode, error_response
from app.api.security import require_user_token
from app.middleware.request_logging import RequestLoggingMiddleware

logger = logging.getLogger(__name__)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app = FastAPI(title="BigBrother API", version="1.0.0")

app.add_middleware(RequestLoggingMiddleware)


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
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    market_index_router,
    prefix="/api/v1",
    dependencies=[Depends(require_user_token)],
)
app.include_router(login_router, prefix="/api/v1")

app.include_router(
    config_router,
    prefix="/api/v1",
    dependencies=[Depends(require_user_token)],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
