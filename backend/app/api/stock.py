"""查询、校验并返回股票资料。"""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.exceptions import ProviderUnavailable
from app.core.logger import observe_provider
from app.core.response import ApiResponse, success_response
from app.core.symbols import stock_exchange
from app.models.stock.model import StockInfo
from app.models.stock.provider import StockProvider

from ._shared import Symbol


router = APIRouter()
provider = StockProvider()


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


def get_stock(symbol: str) -> StockInfo:
    exchange = stock_exchange(symbol)

    source = provider
    with observe_provider(source.name, "stock", symbol=symbol, version=source.version):
        info = source.get_stock_info(symbol)
        if info.symbol != symbol or info.exchange != exchange or not info.name.strip():
            raise ProviderUnavailable("股票代码、交易所或名称校验失败")
        return info


@router.get("/{symbol}", response_model=ApiResponse[StockResponse], summary="股票信息")
def stock(symbol: Symbol) -> ApiResponse[StockResponse]:
    info = get_stock(symbol)
    return success_response(StockResponse(
        **asdict(info),
        source=provider.name,
        source_version=provider.version,
        available_sources=(provider.name,),
        configured_sources=(provider.name,),
    ))
