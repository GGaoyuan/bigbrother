from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v2.router import router as desktop_router
from app.base.api_response import ApiResponse

# CORS 白名单（dev 模式：vite 1420 是 desktop，5173 是 webfront；打包 Tauri 用 tauri://localhost）
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:1420",
    "http://127.0.0.1:1420",
    "tauri://localhost",
    "https://tauri.localhost",
]

app = FastAPI(title="BigBrother API", version="2.0.0", description="v2: 桌面端")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(desktop_router, prefix="/api/v2")


@app.get("/")
async def root():
    return ApiResponse.ok({"message": "BigBrother API", "v2": "desktop"})


@app.get("/health")
async def health_check():
    return ApiResponse.ok({"status": "healthy"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
