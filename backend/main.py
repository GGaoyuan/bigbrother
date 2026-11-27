from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as stocks_router
from app.api.errors import exception_handlers
from app.core.request_logging import RequestLoggingMiddleware
from app.models.provider import MarketDataProvider
from app.services.adjustment_service import AdjustmentService
from app.services.kline_service import KlineService
from app.services.stock_service import StockInfoService
from app.services.volume_profile_service import VolumeProfileService


class LoggedFastAPI(FastAPI):
    def build_middleware_stack(self):
        return RequestLoggingMiddleware(super().build_middleware_stack())


app = LoggedFastAPI(title="BigBrother API", version="1.0.0", exception_handlers=exception_handlers)

provider = MarketDataProvider()
adjustment = AdjustmentService(provider)
stocks = StockInfoService(provider)
klines = KlineService(provider, adjustment)
profiles = VolumeProfileService(klines, stocks, adjustment)
app.state.stocks = stocks
app.state.klines = klines
app.state.profile = profiles


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
