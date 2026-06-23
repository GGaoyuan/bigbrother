from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.base.api_response import ApiResponse
from app.base.user_auth import verify_auth
from app.service.tdx import get_tdx_kline, get_tdx_realtime_quotes

router = APIRouter(prefix="/tdx", tags=["v2-tdx"])


class TdxQuotesRequest(BaseModel):
    symbols: List[str]  # 6 位证券代码列表，如 ["000001", "600000"]


class TdxKlineRequest(BaseModel):
    symbol: str  # 6 位证券代码，如 "600000"
    offset: int = 60  # 返回最近多少根日线


@router.post("/quotes")
async def get_tdx_quotes_api(body: TdxQuotesRequest, _auth=Depends(verify_auth)):
    """通达信实时行情快照（直连行情服务器，不缓存）。"""
    try:
        data = await get_tdx_realtime_quotes(body.symbols)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))


@router.post("/kline")
async def get_tdx_kline_api(body: TdxKlineRequest, _auth=Depends(verify_auth)):
    """通达信日线 K 线（按代码 DAILY 缓存）。"""
    try:
        data = await get_tdx_kline(body.symbol, body.offset)
        return ApiResponse.ok(data)
    except Exception as e:
        return ApiResponse.error(500, str(e))
