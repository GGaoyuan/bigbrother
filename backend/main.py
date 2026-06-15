from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.forward.forward import router as forward_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.breadth import router as breadth_router
from app.api.v1.capital import router as capital_router
from app.api.v1.market import router as market_router
from app.api.v1.sector import router as sector_router
from app.base.api_response import ApiResponse
from app.config.config import settings

app = FastAPI(title="A-Stock Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forward_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(breadth_router, prefix="/api/v1")
app.include_router(sector_router, prefix="/api/v1")
app.include_router(capital_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")


@app.get("/")
async def root():
    return ApiResponse.ok({"message": "A-Stock Analysis API"})


@app.get("/health")
async def health_check():
    return ApiResponse.ok({"status": "healthy"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
