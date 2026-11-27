"""通过 easy_tdx 读取股票资料、历史 K 线和除权事件，并读取 XSHG 交易日历。"""

from collections.abc import Callable
from datetime import date, datetime
from fractions import Fraction
from importlib.metadata import version as package_version
from math import isfinite
from time import monotonic
from typing import TypeVar

from easy_tdx import MacClient, Market, Period, TdxClient
from easy_tdx.mac.enums import Adjust
from exchange_calendars import get_calendar
from exchange_calendars.exchange_calendar_xshg import XSHGExchangeCalendar

from app.core.exceptions import ProviderUnavailable, StockNotFound, UnsupportedMarketData
from app.core.market_time import candle_span
from app.core.symbols import stock_board, stock_exchange

from .model import Adjustment, Candle, CorporateAction, Interval, StockInfo, TradingCalendar


MAC_SERVERS = ("121.36.248.138", "123.60.47.136", "121.37.207.165")
TDX_SERVERS = ("110.41.147.114", "119.97.185.59")
MARKETS = {"SSE": Market.SH, "SZSE": Market.SZ, "BSE": Market.BJ}
PERIODS = {
    "day": Period.DAILY, "week": Period.WEEKLY, "month": Period.MONTHLY,
    "1m": Period.MIN_1, "5m": Period.MIN_5, "60m": Period.MIN_60,
}
PAGE_SIZE = 700
MAX_PAGES = 128
QUERY_TIMEOUT = 18
SHARE_QUANTUM = 100
Result = TypeVar("Result")


def _normalize(row: dict, interval: Interval) -> Candle:
    label = datetime.fromisoformat(str(row["datetime"]))
    if label.second or label.microsecond:
        raise ProviderUnavailable("MAC 行情返回未对齐的 K 线时间")
    timestamp, end = candle_span(label, interval, right_labeled=True)
    opening, high, low, close = (round(float(row[field]), 2) for field in ("open", "high", "low", "close"))

    native_volume = float(row["vol"])
    precision = SHARE_QUANTUM if interval == "1m" else 1
    if not isfinite(native_volume) or native_volume < 0 or native_volume % precision:
        raise ProviderUnavailable("MAC 行情成交量不符合该周期的股数粒度")
    volume = int(native_volume)
    # MAC 行情的成交额和按固定粒度发布的成交量各自编码。
    # 1 分钟线使用已验证的股数。其他周期仅保留能与股数和价格核对的成交额。
    amount = None
    if interval != "1m" and volume and row.get("amount") is not None:
        candidate = float(row["amount"])
        if isfinite(candidate) and candidate > 0 and low - 0.01 <= candidate / volume <= high + 0.01:
            amount = candidate
    return Candle(timestamp, end, opening, high, low, close, volume, amount, "shares", volume, precision)


def _action_value(row: dict, field: str, multiplier: int = 1) -> Fraction:
    value = row[field]
    if type(value) not in (int, float) or not isfinite(value) or value < 0:
        raise ValueError(field)
    return Fraction(str(value * multiplier))


def _read_actions(client: TdxClient, market: Market, symbol: str) -> tuple[CorporateAction, ...]:
    rows = client.get_xdxr_info(market, symbol).to_dict("records")
    if not rows:
        raise ProviderUnavailable("通达信未返回可核验的除权除息记录")

    actions = []
    try:
        for row in rows:
            if type(row.get("category")) is not int or row["category"] < 1:
                raise ValueError("category")
            ex_date = date.fromisoformat(str(row["date"])[:10])
            if row["category"] == 1:
                # easy_tdx 输出每股红利、送转和配股比例，模型统一使用每 10 股口径。
                actions.append(CorporateAction(
                    ex_date=ex_date,
                    cash_dividend=_action_value(row, "fenhong", 10),
                    bonus_shares=_action_value(row, "songzhuangu", 10),
                    rights_shares=_action_value(row, "peigu", 10),
                    rights_price=_action_value(row, "peigujia"),
                ))
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ProviderUnavailable("通达信除权除息记录格式异常") from exc
    return tuple(actions)


class MarketDataProvider:
    name = "easy-tdx"
    version = package_version("easy-tdx")
    calendar_name = "exchange-calendars-xshg"
    calendar_version = package_version("exchange-calendars")

    def __init__(
        self, mac_servers: tuple[str, ...] = MAC_SERVERS, tdx_servers: tuple[str, ...] = TDX_SERVERS,
    ):
        self._mac_servers = mac_servers
        self._tdx_servers = tdx_servers

    @staticmethod
    def _fetch(
        client_type: type[MacClient] | type[TdxClient], servers: tuple[str, ...], operation: str,
        read: Callable[..., Result],
    ) -> Result:
        deadline = monotonic() + QUERY_TIMEOUT
        last_error = None
        for host in servers:
            remaining = deadline - monotonic()
            if remaining <= 0:
                break
            try:
                with client_type(host, port=7709, timeout=min(3, remaining), auto_reconnect=False,
                                 heartbeat_interval=0) as client:
                    return read(client, deadline)
            except Exception as exc:
                last_error = exc
        detail = f"：{last_error}" if last_error else ""
        raise ProviderUnavailable(f"通达信{operation}暂不可用{detail}") from last_error

    def get_stock_info(self, symbol: str) -> StockInfo:
        exchange = stock_exchange(symbol)
        market = int(MARKETS[exchange])
        rows = self._fetch(
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

    def get_corporate_actions(self, symbol: str) -> tuple[CorporateAction, ...]:
        market = MARKETS[stock_exchange(symbol)]
        return self._fetch(
            TdxClient, self._tdx_servers, "除权除息",
            lambda client, _: _read_actions(client, market, symbol),
        )

    def get_calendar(self) -> TradingCalendar:
        # 日历库声明的覆盖范围端点可能是非交易日。
        start = XSHGExchangeCalendar.bound_min()
        end = XSHGExchangeCalendar.bound_max()
        try:
            calendar = get_calendar("XSHG", start=start, end=end)
            sessions = tuple(calendar.sessions.date)
        except (TypeError, ValueError, RuntimeError) as exc:
            raise ProviderUnavailable("交易日历暂不可用") from exc
        return TradingCalendar(start.date(), end.date(), sessions)

    def get_klines(
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]:
        if interval not in PERIODS or adjust != "none":
            raise UnsupportedMarketData("MAC K 线只提供支持周期的不复权行情")
        exchange = stock_exchange(symbol)
        if exchange == "BSE":
            raise UnsupportedMarketData("MAC K 线尚未核验北交所证券")
        if limit < 1 or (start is not None and end is not None and start >= end):
            raise UnsupportedMarketData("MAC K 线区间或条数无效")

        return self._fetch(
            MacClient, self._mac_servers, "MAC K 线",
            lambda client, deadline: self._read_klines(
                client, int(MARKETS[exchange]), symbol, interval, start, end, limit, deadline,
            ),
        )

    def _read_klines(self, client, market, symbol, interval, start, end, limit, deadline) -> tuple[Candle, ...]:
        period = PERIODS[interval]
        offset = 0
        size = min(limit, PAGE_SIZE) if start is None and end is None else PAGE_SIZE
        oldest = None
        selected: list[Candle] = []
        for _ in range(MAX_PAGES):
            if monotonic() >= deadline:
                raise ProviderUnavailable("MAC K 线分页超时")
            page = client.get_stock_kline(market, symbol, period, start=offset, count=size, adjust=Adjust.NONE)
            if page.empty:
                if offset == 0:
                    raise ProviderUnavailable("MAC 接口未返回 K 线")
                break

            rows = tuple(_normalize(row, interval) for row in page.to_dict("records"))
            earliest = min(bar.timestamp for bar in rows)
            if oldest is not None and earliest >= oldest:
                raise ProviderUnavailable("MAC K 线分页未向历史推进")
            oldest = earliest
            offset += len(rows)
            selected.extend(
                bar for bar in rows
                if (start is None or bar.end_timestamp > start) and (end is None or bar.timestamp < end)
            )
            if len(selected) >= limit or (start is not None and oldest <= start) or len(rows) < size:
                break
        else:
            raise ProviderUnavailable("MAC K 线超出分页上限")

        return tuple(sorted(selected, key=lambda bar: bar.timestamp)[-limit:])
