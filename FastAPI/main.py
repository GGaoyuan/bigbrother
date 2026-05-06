from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.stock import router as stock_router
from app.api.v1.market_sentiment import router as sentiment_router
from app.core.response import ApiResponse
from app.core.config import settings

app = FastAPI(title="Stock Data API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock_router, prefix="/api/v1")
app.include_router(sentiment_router, prefix="/api/v1")


@app.get("/")
async def root():
    return ApiResponse.ok({"message": "Stock Data API"})


@app.get("/health")
async def health_check():
    return ApiResponse.ok({"status": "healthy"})



if __name__ == '__main__':
    import akshare as ak

    print("测试 akshare 数据获取...")
    try:
        # df = ak.stock_individual_info_em(symbol="000001")
        # df = ak.stock_xgsr_ths()
        df = ak.stock_zygc_em(symbol="000066")

        print(f"✓ 成功获取")
        print(df)
        #
        # print("\n前 3 条数据：")
        # print(df.head(3)[["代码", "名称", "最新价", "涨跌幅"]])
    except Exception as e:
        print(f"✗ 获取失败: {e}")