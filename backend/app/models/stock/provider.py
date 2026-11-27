"""通过 easy_tdx MAC 行情读取个股资料。"""

from importlib.metadata import version as package_version

from easy_tdx import MacClient, Market

from app.core.exceptions import ProviderUnavailable, StockNotFound
from app.core.market_connection import MAC_SERVERS, fetch_market_data
from app.core.symbols import stock_board, stock_exchange

from .model import StockInfo


MARKETS = {"SSE": Market.SH, "SZSE": Market.SZ, "BSE": Market.BJ}


class StockProvider:
    name = "easy-tdx"
    version = package_version("easy-tdx")

    def __init__(self, mac_servers: tuple[str, ...] = MAC_SERVERS):
        self._mac_servers = mac_servers

    def get_stock_info(self, symbol: str) -> StockInfo:
        exchange = stock_exchange(symbol)
        market = int(MARKETS[exchange])
        rows = fetch_market_data(
            MacClient, self._mac_servers, "股票资料",
            lambda client, _: client.get_stock_quotes([(market, symbol)]).to_dict("records"),
        )
        if not rows:
            raise StockNotFound(f"通达信未找到股票 {symbol}")
        row = rows[0]
        name = row.get("name")
        if (len(rows) != 1 or row.get("market") != market or row.get("code") != symbol
                or not isinstance(name, str) or not name.strip()):
            raise ProviderUnavailable("通达信返回的股票资料无效")
        return StockInfo(symbol, name.strip(), exchange, stock_board(symbol))
