from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.forward.forward import router as data_provider_router
from app.api.v1.fundation import router as fundation_router
from app.base.api_response import ApiResponse
from app.config.config import settings
from pytdx.hq import TdxHq_API


app = FastAPI(title="Stock Data API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_provider_router, prefix="/api/v1")
app.include_router(fundation_router, prefix="/api/v1")


@app.get("/")
async def root():
    return ApiResponse.ok({"message": "aaa Data API"})


@app.get("/health")
async def health_check():
    return ApiResponse.ok({"status": "healthy"})



# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)


if __name__ == '__main__':
    pass