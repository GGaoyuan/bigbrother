"""Read raw index market data from Tongdaxin servers through mootdx."""

from functools import lru_cache
from threading import Lock

from mootdx.quotes import Quotes
from pandas import DataFrame

_CLIENT_LOCK = Lock()


@lru_cache(maxsize=1)
def _client() -> Quotes:
    return Quotes.factory(market="std")


def get_index_daily_kline(symbol: str) -> DataFrame | None:
    """通过通达信获取指数最近最多 800 根原始日 K 线。

    Args:
        symbol: 六位指数代码；000001 为上证指数，000300 为沪深300。
    """
    with _CLIENT_LOCK:
        return _client().index(
            symbol=symbol,
            frequency=9,
            start=0,
            offset=800,
        )
