"""Stock name and exchange lookup."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.response import ApiResponse, success_response

from ._shared import StockServiceDependency, Symbol


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


@router.get("/{symbol}", response_model=ApiResponse[StockResponse], summary="股票信息")
def stock(symbol: Symbol, service: StockServiceDependency) -> ApiResponse[StockResponse]:
    result = service.get_stock(symbol)
    return success_response(StockResponse(
        **asdict(result.stock),
        source=result.source,
        source_version=result.source_version,
        available_sources=result.available_sources,
        configured_sources=result.configured_sources,
    ))
