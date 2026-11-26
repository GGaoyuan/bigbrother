from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import exception_handlers
from app.api.stocks import router as stocks_router
from app.core.request_logging import RequestLoggingMiddleware
from app.data.easy_tdx_minutes import EasyTdxMinuteData
from app.data.tdx import (
    TdxConnection, TdxCorporateActionData, TdxKlineData, TdxStockData,
)
from app.data.tencent import TencentKlineData, TencentStockData
from app.data.xshg_calendar import XshgCalendarData
from app.services.adjustment import AdjustmentService
from app.services.klines import KlineService
from app.services.stock_info import StockInfoService
from app.services.volume_profile import VolumeProfileService


class LoggedFastAPI(FastAPI):
    def build_middleware_stack(self):
        return RequestLoggingMiddleware(super().build_middleware_stack())


app = LoggedFastAPI(title="BigBrother API", version="1.0.0", exception_handlers=exception_handlers)

tdx_connection = TdxConnection()
tdx_klines = TdxKlineData(tdx_connection)
tencent_klines = TencentKlineData()
adjustment = AdjustmentService(TdxCorporateActionData(tdx_connection))
stocks = StockInfoService((TdxStockData(tdx_connection), TencentStockData()))
klines = KlineService((tdx_klines, tencent_klines), adjustment)
profiles = VolumeProfileService(
    klines, stocks, adjustment,
    (tdx_klines, EasyTdxMinuteData(), tencent_klines),
    XshgCalendarData(),
)
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
