"""查询股票名称和所属交易所。"""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.core.response import ApiResponse, success_response
from app.services.stock_service import StockService

from ._shared import Symbol


router = APIRouter()


class StockResponse(BaseModel):
    symbol: str
    name: str
    exchange: str
    market: str
    currency: str
    price_tick: float
    source: str
    source_version: str
    available_sources: tuple[str, ...]
    configured_sources: tuple[str, ...]


def get_service(request: Request) -> StockService:
    return request.app.state.stocks


@router.get("/{symbol}", response_model=ApiResponse[StockResponse], summary="股票信息")
def stock(symbol: Symbol, service: Annotated[StockService, Depends(get_service)]) -> ApiResponse[StockResponse]:
    result = service.get_stock(symbol)
    return success_response(StockResponse(
        **asdict(result.stock),
        source=result.source,
        source_version=result.source_version,
        available_sources=result.available_sources,
        configured_sources=result.configured_sources,
    ))
