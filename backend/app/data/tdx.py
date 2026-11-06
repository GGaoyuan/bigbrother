"""Read raw index market data from Tongdaxin servers through mootdx."""

from functools import lru_cache
from threading import Lock

from mootdx.quotes import Quotes
from pandas import DataFrame

_CLIENT_LOCK = Lock()


@lru_cache(maxsize=1)
def _client() -> Quotes:
    return Quotes.factory(market="std")


def get_shanghai_index_daily_kline(limit: int = 500) -> DataFrame | None:
    """Fetch raw daily bars for the Shanghai Composite.

    Args:
        limit: Number of latest bars to request, up to 800.
    """
    with _CLIENT_LOCK:
        return _client().index(
            symbol="000001",
            frequency=9,
            start=0,
            offset=limit,
        )
