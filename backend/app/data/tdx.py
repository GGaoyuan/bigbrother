"""A-share metadata, raw candles and adjustment events from mootdx."""

from collections.abc import Callable, Mapping
from datetime import date, datetime
from fractions import Fraction
from importlib.metadata import version
from math import isfinite
from threading import Lock
from time import monotonic
from typing import TypeVar

import mootdx
from tdxpy.exceptions import TdxConnectionError
from tdxpy.hq import TdxHq_API
from tdxpy.parser.base import (
    ResponseHeaderRecvFails, ResponseRecvFails, SendRequestPkgFails, SocketClientNotReady,
)

from app.core.exceptions import ProviderUnavailable, StockNotFound, UnsupportedMarketData
from app.core.logger import log_provider
from app.core.market_time import CHINA, candle_span
from app.core.symbols import stock_board, stock_exchange
from app.models.corporate_action import CorporateAction
from app.models.kline import Adjustment, Candle, Interval, VolumeUnit
from app.models.stock import StockInfo


SERVERS = (("110.41.147.114", 7709), ("119.97.185.59", 7709))
FREQUENCIES = {"day": 9, "week": 5, "month": 6, "1m": 8, "5m": 0, "60m": 3}
SHARES_PER_LOT = 100
CANDLE_PAGE_SIZE = 800
MAX_CANDLE_PAGES = 24
SECURITY_PAGE_SIZE = 1000
MAX_SECURITIES = 40000
MAX_SECURITY_PAGES = 80
DIRECTORY_TTL = 3600
FAILURE_COOLDOWN = 120
TRANSPORT_ERRORS = (
    OSError, TdxConnectionError, ResponseHeaderRecvFails, ResponseRecvFails,
    SendRequestPkgFails, SocketClientNotReady,
)
Result = TypeVar("Result")


def _market(exchange: str) -> int:
    if exchange == "BSE":
        raise UnsupportedMarketData("通达信公共行情接口不支持北交所 A 股")
    return int(exchange == "SSE")


def _read_directory(client: TdxHq_API, market: int, exchange: str) -> dict[str, StockInfo]:
    count = int(client.get_security_count(market))
    if not 0 < count <= MAX_SECURITIES:
        raise ProviderUnavailable("通达信证券目录数量异常")

    received = 0
    matches: dict[str, StockInfo] = {}
    pages = set()
    for _ in range(MAX_SECURITY_PAGES):
        rows = client.get_security_list(market, received)
        if not rows:
            break
        if len(rows) > SECURITY_PAGE_SIZE:
            raise ProviderUnavailable("通达信证券目录分页数量异常")
        keys = tuple(str(row["code"]) for row in rows)
        if keys in pages:
            raise ProviderUnavailable("通达信证券目录返回重复分页")
        pages.add(keys)
        received += len(rows)

        for row, symbol in zip(rows, keys):
            try:
                if stock_exchange(symbol) != exchange:
                    continue
            except StockNotFound:
                continue
            name = str(row["name"]).rstrip("\x00 ")
            if name:
                matches[symbol] = StockInfo(symbol, name, exchange, stock_board(symbol))
        if received >= count:
            break

    if received < count or not matches:
        raise ProviderUnavailable("通达信证券目录未完整返回")
    return matches


def _bar_volume(raw: float, amount: float | None, low: float, high: float) -> tuple[int, VolumeUnit]:
    if not isfinite(raw) or raw < 0 or abs(raw - round(raw)) > 0.001:
        raise ProviderUnavailable("通达信 K 线成交量格式异常")
    volume = round(raw)
    if not volume and not amount:
        return 0, "unknown"

    def can_be_shares(shares: int) -> bool:
        if not shares or not amount:
            return False
        average = amount / shares
        return low - 0.01 <= average <= high + 0.01

    if can_be_shares(volume):
        return volume, "shares"
    if can_be_shares(volume * SHARES_PER_LOT):
        return volume * SHARES_PER_LOT, "lots"
    raise ProviderUnavailable("无法通过成交额核实通达信 K 线成交量单位")


def _normalize_candle(row: dict, interval: Interval, symbol: str) -> Candle:
    label = datetime.fromisoformat(str(row["datetime"]))
    timestamp, end_timestamp = candle_span(label, interval, right_labeled=True)
    opening, high, low, close = (float(row[key]) for key in ("open", "high", "low", "close"))
    amount_value = row.get("amount")
    amount = float(amount_value) if amount_value is not None else None
    if not all(isfinite(price) for price in (opening, high, low, close)) or not (
        0 < low <= min(opening, close) <= max(opening, close) <= high
    ):
        raise ProviderUnavailable("通达信 K 线价格异常")
    if amount is not None and (not isfinite(amount) or amount < 0):
        raise ProviderUnavailable("通达信 K 线成交额异常")
    volume, unit = _bar_volume(float(row["vol"]), amount, low, high)
    if unit == "lots" and symbol.startswith(("688", "689")):
        unit = "rounded_lots"
    return Candle(timestamp, end_timestamp, opening, high, low, close, volume, amount, unit, float(row["vol"]))


def _candles(
    client: TdxHq_API, symbol: str, market: int, interval: Interval,
    start: int | None, end: int | None, limit: int,
) -> tuple[Candle, ...]:
    candles: dict[int, Candle] = {}
    minute_rows: list[Candle] = []
    cursor = 0
    previous_oldest: int | None = None
    page_size = min(CANDLE_PAGE_SIZE, limit) if end is None else CANDLE_PAGE_SIZE

    for _ in range(MAX_CANDLE_PAGES):
        rows = client.get_security_bars(FREQUENCIES[interval], market, symbol, cursor, page_size)
        if not rows:
            if cursor == 0:
                raise ProviderUnavailable("通达信公共行情主站未返回 K 线")
            break
        page = [_normalize_candle(row, interval, symbol) for row in rows]
        oldest = min(bar.timestamp for bar in page)
        if previous_oldest is not None and oldest >= previous_oldest:
            raise ProviderUnavailable("通达信 K 线分页未推进")
        previous_oldest = oldest
        cursor += len(page)

        for bar in page:
            if (start is not None and bar.end_timestamp <= start) or (end is not None and bar.timestamp >= end):
                continue
            if interval == "1m":
                minute_rows.append(bar)
                continue
            previous = candles.get(bar.timestamp)
            if previous is not None and previous != bar:
                raise ProviderUnavailable("通达信 K 线重复时间记录存在冲突")
            candles[bar.timestamp] = bar
        if len(candles) >= limit or len(minute_rows) >= limit or (start is not None and oldest <= start) or len(page) < page_size:
            break
    else:
        raise ProviderUnavailable("通达信未在分页上限内返回所需 K 线区间")

    result = minute_rows if interval == "1m" else candles.values()
    return tuple(sorted(result, key=lambda bar: bar.timestamp)[-limit:])


class TdxConnection:
    name = "mootdx"
    version = f"{mootdx.__version__}+tdxpy.{version('tdxpy')}-stock-v2"

    def __init__(self, servers: tuple[tuple[str, int], ...] = SERVERS, timeout: float = 3):
        self._servers = servers
        self._timeout = timeout
        self.lock = Lock()
        self._clients: dict[tuple[str, int], TdxHq_API] = {}
        self._cooldown: dict[tuple[tuple[str, int], str], float] = {}

    @staticmethod
    def _close_client(client: TdxHq_API) -> None:
        try:
            client.disconnect()
        except Exception:
            pass

    def _connect(self, server: tuple[str, int]) -> TdxHq_API:
        # Use mootdx's transport without unbounded server discovery or retries.
        client = TdxHq_API(auto_retry=False, raise_exception=True)
        try:
            client.connect(*server, time_out=self._timeout)
        except Exception:
            self._close_client(client)
            raise
        self._clients[server] = client
        return client

    def query_locked(self, capability: str, call: Callable[[TdxHq_API], Result]) -> Result:
        last_error: Exception | None = None
        for server in self._servers:
            now = monotonic()
            address = f"{server[0]}:{server[1]}"
            if max(self._cooldown.get((server, "connect"), 0), self._cooldown.get((server, capability), 0)) > now:
                log_provider("server_skipped", self.name, capability, server=address, reason="cooldown")
                continue
            log_provider("server_attempt", self.name, capability, server=address)
            for _ in range(2):
                client = self._clients.get(server)
                reused = client is not None
                if client is None:
                    try:
                        client = self._connect(server)
                    except Exception as exc:
                        self._cooldown[server, "connect"] = monotonic() + FAILURE_COOLDOWN
                        last_error = exc
                        log_provider(
                            "server_failed", self.name, capability, server=address,
                            stage="connect", reason=str(exc),
                        )
                        break

                try:
                    result = call(client)
                except Exception as exc:
                    last_error = exc
                    error = getattr(exc, "original_exception", exc)
                    log_provider("server_failed", self.name, capability, server=address,
                                 stage="query", reason=str(error))
                    if isinstance(error, TRANSPORT_ERRORS):
                        self._clients.pop(server, None)
                        self._close_client(client)
                        if reused:
                            log_provider("server_reconnect", self.name, capability, server=address)
                            continue
                    if not isinstance(exc, ProviderUnavailable):
                        self._cooldown[server, capability] = monotonic() + FAILURE_COOLDOWN
                    break
                else:
                    log_provider("server_selected", self.name, capability, server=address)
                    return result

        detail = f"：{last_error}" if isinstance(last_error, ProviderUnavailable) else ""
        raise ProviderUnavailable(f"通达信公共行情主站的{capability}暂不可用{detail}") from last_error


class TdxStockData:
    name = TdxConnection.name
    version = TdxConnection.version

    def __init__(self, connection: TdxConnection):
        self._connection = connection
        self._directories: dict[str, tuple[float, dict[str, StockInfo]]] = {}

    def get_stock_info(self, symbol: str) -> StockInfo:
        exchange = stock_exchange(symbol)
        market = _market(exchange)
        with self._connection.lock:
            directory = self._directories.get(exchange)
            if directory is None or directory[0] <= monotonic():
                stocks = self._connection.query_locked("证券目录", lambda client: _read_directory(client, market, exchange))
                self._directories[exchange] = (monotonic() + DIRECTORY_TTL, stocks)
            else:
                stocks = directory[1]
        if symbol not in stocks:
            raise StockNotFound(f"通达信证券目录中未找到 {symbol}")
        return stocks[symbol]


class TdxKlineData:
    name = TdxConnection.name
    version = TdxConnection.version
    minute_history_limit: int | None = None

    def __init__(self, connection: TdxConnection):
        self._connection = connection

    def get_klines(
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]:
        market = _market(stock_exchange(symbol))
        if interval not in FREQUENCIES or limit < 1:
            raise UnsupportedMarketData("通达信 K 线周期或条数无效")
        if adjust != "none":
            raise UnsupportedMarketData("通达信公共行情主站仅提供经核验的不复权 K 线接口")
        with self._connection.lock:
            return self._connection.query_locked("1 分钟 K 线" if interval == "1m" else "K 线", lambda client: _candles(client, symbol, market, interval, start, end, limit))


def _action_value(row: Mapping, field: str) -> Fraction:
    value = row[field]
    if type(value) not in (int, float) or not isfinite(value) or value < 0:
        raise ValueError(field)
    return Fraction(str(value))


def normalize_actions(rows: object) -> tuple[CorporateAction, ...]:
    # A short tdxpy response can decode as an empty list. A verified payload
    # with only non-price events is sufficient to establish identity adjustment.
    if not isinstance(rows, (list, tuple)) or not rows:
        raise ProviderUnavailable("通达信未返回可核验的除权除息记录")

    actions: list[CorporateAction] = []
    try:
        for row in rows:
            if not isinstance(row, Mapping) or type(row.get("category")) is not int or row["category"] < 1:
                raise ValueError("category")
            event_day = date(row["year"], row["month"], row["day"])
            if row["category"] == 1:
                actions.append(CorporateAction(
                    ex_date=event_day,
                    cash_dividend=_action_value(row, "fenhong"),
                    bonus_shares=_action_value(row, "songzhuangu"),
                    rights_shares=_action_value(row, "peigu"),
                    rights_price=_action_value(row, "peigujia"),
                ))
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ProviderUnavailable("通达信除权除息记录格式异常") from exc
    return tuple(actions)


class TdxCorporateActionData:
    name = TdxConnection.name
    version = TdxConnection.version

    def __init__(self, connection: TdxConnection):
        self._connection = connection

    def get_corporate_actions(self, symbol: str) -> tuple[CorporateAction, ...]:
        market = _market(stock_exchange(symbol))
        with self._connection.lock:
            return self._connection.query_locked(
                "除权除息",
                lambda client: normalize_actions(client.get_xdxr_info(market, symbol)),
            )
