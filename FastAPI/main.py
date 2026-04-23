from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.stock import router as stock_router
from app.api.v1.market_sentiment import router as sentiment_router
from app.schemas.response import ApiResponse
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
