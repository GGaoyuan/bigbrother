from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as stocks_router
from app.api.errors import exception_handlers
from app.core.request_logging import RequestLoggingMiddleware


class LoggedFastAPI(FastAPI):
    def build_middleware_stack(self):
        return RequestLoggingMiddleware(super().build_middleware_stack())


app = LoggedFastAPI(title="BigBrother API", version="1.0.0", exception_handlers=exception_handlers)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(?:localhost|127\.0\.0\.1)(?::\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
