"""A-share metadata, raw candles and historical transaction slices from mootdx."""

from collections.abc import Callable
from datetime import date, datetime, time
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

from app.console_logging import log_provider
from app.data.stock_adjustment import AdjustmentFactors, build_tdx_qfq
from app.data.stock_market_types import (
    CHINA,
    Adjustment,
    Candle,
    Interval,
    ProviderUnavailable,
    StockInfo,
    StockNotFound,
    Tick,
    TickCoverage,
    TickDay,
    UnsupportedMarketData,
    candle_span,
    stock_board,
    stock_exchange,
)


SERVERS = (("110.41.147.114", 7709), ("119.97.185.59", 7709))
FREQUENCIES = {"day": 9, "week": 5, "month": 6, "1m": 8, "5m": 0, "60m": 3}
SHARES_PER_LOT = 100
CANDLE_PAGE_SIZE = 800
TICK_PAGE_SIZE = 2000
MAX_CANDLE_PAGES = 24
MAX_TICK_PAGES = 8
SECURITY_PAGE_SIZE = 1000
MAX_SECURITIES = 40000
MAX_SECURITY_PAGES = 80
DIRECTORY_TTL = 3600
FAILURE_COOLDOWN = 120
TICK_RESOLUTION = "aggregated_minute_label"
SESSION_CLOSE = time(15)
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


def _bar_volume(raw: float, amount: float | None, low: float, high: float) -> tuple[int, str]:
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


def _ticks(client: TdxHq_API, symbol: str, market: int, day: date) -> TickDay:
    requested = int(day.strftime("%Y%m%d"))
    cursor = 0
    pages: list[list[Tick]] = []
    signatures: set[tuple[Tick, ...]] = set()
    ended = False
    for _ in range(MAX_TICK_PAGES):
        rows = client.get_history_transaction_data(market, symbol, cursor, TICK_PAGE_SIZE, requested)
        if not rows:
            ended = True
            break

        page: list[Tick] = []
        for row in rows:
            minute = time.fromisoformat(row["time"])
            timestamp = int(datetime.combine(day, minute, CHINA).timestamp())
            price = float(row["price"])
            lots = float(row["vol"])
            if not isfinite(price) or price <= 0 or not isfinite(lots) or lots < 0 or not lots.is_integer():
                raise ProviderUnavailable("通达信历史分笔价格或成交量异常")
            side = {0: "BUY", 1: "SELL"}.get(row["buyorsell"], "UNKNOWN")
            page.append(Tick(timestamp, price, int(lots) * SHARES_PER_LOT, None, side))

        signature = tuple(page)
        if signature in signatures:
            break
        signatures.add(signature)
        pages.append(page)
        cursor += len(page)

    ticks = tuple(tick for page in reversed(pages) for tick in page)
    unit = "rounded_lots" if symbol.startswith(("688", "689")) else "lots"
    reason = "通达信没有返回该日的历史分笔数据"
    complete = False
    verified_until = None
    if ticks:
        closing_timestamp = int(datetime.combine(day, SESSION_CLOSE, CHINA).timestamp())
        regular = tuple(tick for tick in ticks if tick.timestamp <= closing_timestamp)
        if not ended or any(a.timestamp > b.timestamp for a, b in zip(ticks, ticks[1:])):
            reason = "未确认通达信历史分笔分页完整"
        elif datetime.now(CHINA) < datetime.combine(day, time(15, 31), CHINA):
            reason = "交易日尚未结束，历史分笔可能不完整"
        else:
            try:
                minute_rows = client.get_history_minute_time_data(market, symbol, requested)
            except Exception:
                minute_rows = None
            if not minute_rows or len(minute_rows) != 240 or not regular:
                reason = "缺少可用于收盘成交量对账的历史分时"
            elif (
                sum(tick.volume for tick in regular) != sum(row["vol"] for row in minute_rows) * SHARES_PER_LOT
                or abs(regular[-1].price - float(minute_rows[-1]["price"])) > 0.005
            ):
                reason = "历史分笔与历史分时的收盘价或成交量未对账"
            else:
                complete = True
                verified_until = closing_timestamp + 60
                reason = "常规交易成交量与通达信历史分时对账一致；分钟标记聚合记录无法精确还原成交价量及成交额，盘后未独立核验"

    nonzero_ticks = tuple(tick for tick in ticks if tick.volume > 0)
    omitted = len(ticks) - len(nonzero_ticks)
    if omitted:
        reason += f"；省略 {omitted} 条零手聚合记录，其实际股数无法还原"
    return TickDay(
        day, nonzero_ticks, complete and bool(nonzero_ticks), TICK_RESOLUTION,
        unit, False, reason, omitted_zero_lot_rows=omitted, verified_until=verified_until,
    )


class TdxProvider:
    minute_historical_queries = True
    name = "mootdx"
    version = f"{mootdx.__version__}+tdxpy.{version('tdxpy')}-stock-v2"

    def __init__(self, servers: tuple[tuple[str, int], ...] = SERVERS, timeout: float = 3):
        self._servers = servers
        self._timeout = timeout
        self._lock = Lock()
        self._clients: dict[tuple[str, int], TdxHq_API] = {}
        self._cooldown: dict[tuple[tuple[str, int], str], float] = {}
        self._directories: dict[str, tuple[float, dict[str, StockInfo]]] = {}

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

    def _query(self, capability: str, call: Callable[[TdxHq_API], Result]) -> Result:
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

    def get_stock_info(self, symbol: str) -> StockInfo:
        exchange = stock_exchange(symbol)
        market = _market(exchange)
        with self._lock:
            directory = self._directories.get(exchange)
            if directory is None or directory[0] <= monotonic():
                stocks = self._query("证券目录", lambda client: _read_directory(client, market, exchange))
                self._directories[exchange] = (monotonic() + DIRECTORY_TTL, stocks)
            else:
                stocks = directory[1]
        if symbol not in stocks:
            raise StockNotFound(f"通达信证券目录中未找到 {symbol}")
        return stocks[symbol]

    def get_adjustment_factors(self, symbol: str) -> AdjustmentFactors:
        market = _market(stock_exchange(symbol))
        as_of = datetime.now(CHINA).date()
        with self._lock:
            return self._query(
                "除权除息",
                lambda client: build_tdx_qfq(client.get_xdxr_info(market, symbol), as_of=as_of),
            )

    def get_klines(
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]:
        market = _market(stock_exchange(symbol))
        if interval not in FREQUENCIES or limit < 1:
            raise UnsupportedMarketData("通达信 K 线周期或条数无效")
        if adjust != "none":
            raise UnsupportedMarketData("通达信公共行情主站仅提供经核验的不复权 K 线接口")
        with self._lock:
            return self._query("1 分钟 K 线" if interval == "1m" else "K 线", lambda client: _candles(client, symbol, market, interval, start, end, limit))

    def get_ticks(self, symbol: str, day: date) -> TickDay:
        market = _market(stock_exchange(symbol))
        if day > datetime.now(CHINA).date():
            raise UnsupportedMarketData("无法查询未来日期的通达信历史分笔")
        with self._lock:
            return self._query("历史分笔", lambda client: _ticks(client, symbol, market, day))

    def get_tick_coverage(self, symbol: str) -> TickCoverage:
        _market(stock_exchange(symbol))
        return TickCoverage(
            None, None, None, True, True, False, TICK_RESOLUTION,
            "通达信公共主站返回按分钟标记的历史分笔聚合，连续覆盖范围须逐日核验",
        )

    def health_check(self) -> bool:
        with self._lock:
            try:
                return self._query("证券数量", lambda client: int(client.get_security_count(1)) > 0)
            except ProviderUnavailable:
                return False
