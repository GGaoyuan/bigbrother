"""Request unadjusted historical 1-minute stock bars through easy_tdx's MAC client."""

from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from math import isfinite
from time import monotonic

from app.console_logging import log_provider
from app.data.stock_market_types import (
    Adjustment, Candle, Interval, ProviderUnavailable, UnsupportedMarketData, candle_span, stock_exchange,
)


try:
    from easy_tdx import MacClient, Period
    from easy_tdx.mac.enums import Adjust
except ModuleNotFoundError as exc:
    if exc.name != "easy_tdx":
        raise
    MacClient = Period = Adjust = None

try:
    SDK_VERSION = version("easy-tdx")
except PackageNotFoundError:
    SDK_VERSION = "unavailable"


SERVERS = ("121.36.248.138", "123.60.47.136", "121.37.207.165")
PAGE_SIZE = 700
MAX_PAGES = 128
QUERY_TIMEOUT = 18
SHARE_QUANTUM = 100


def _normalize(row: dict) -> Candle:
    label = datetime.fromisoformat(str(row["datetime"]))
    if label.second or label.microsecond:
        raise ProviderUnavailable("MAC 行情返回未对齐的分钟时间")
    timestamp, end = candle_span(label, "1m", right_labeled=True)
    prices = tuple(round(float(row[field]), 2) for field in ("open", "high", "low", "close"))
    opening, high, low, close = prices
    if not all(isfinite(price) for price in prices) or not (
        0 < low <= min(opening, close) <= max(opening, close) <= high
    ):
        raise ProviderUnavailable("MAC 行情返回无效的分钟 OHLC")

    native_volume = float(row["vol"])
    if not isfinite(native_volume) or native_volume < 0 or native_volume % SHARE_QUANTUM:
        raise ProviderUnavailable("MAC 行情成交量不符合已核验的 100 股粒度")
    volume = int(native_volume)
    # MAC turnover and its quantized volume are independently encoded.
    # Only the reported share count is used for volume-at-price calculations.
    return Candle(timestamp, end, opening, high, low, close, volume, None, "shares", volume, SHARE_QUANTUM)


class EasyTdxMinuteProvider:
    name = "easy-tdx-mac"
    version = f"{SDK_VERSION}-mac-minute-v1"
    minute_historical_queries = True

    def __init__(self, servers: tuple[str, ...] = SERVERS):
        self._servers = servers

    def get_klines(
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]:
        if interval != "1m" or adjust != "none":
            raise UnsupportedMarketData("MAC 行情适配器只提供不复权 1 分钟 K 线")
        exchange = stock_exchange(symbol)
        if exchange == "BSE":
            raise UnsupportedMarketData("MAC 分钟行情尚未核验北交所证券")
        if limit < 1 or (start is not None and end is not None and start >= end):
            raise UnsupportedMarketData("MAC 分钟行情区间或条数无效")

        if MacClient is None:
            raise ProviderUnavailable("历史分钟行情 SDK easy_tdx 未安装")
        market = int(exchange == "SSE")
        deadline = monotonic() + QUERY_TIMEOUT
        last_error = None
        for host in self._servers:
            remaining = deadline - monotonic()
            if remaining <= 0:
                break
            address = f"{host}:7709"
            log_provider("server_attempt", self.name, "profile_minutes", server=address, symbol=symbol)
            try:
                with MacClient(host, port=7709, timeout=min(3, remaining), auto_reconnect=False,
                               heartbeat_interval=0) as client:
                    rows = self._read(client, market, symbol, start, end, limit, deadline)
            except Exception as exc:
                last_error = exc
                log_provider("server_failed", self.name, "profile_minutes", server=address,
                             symbol=symbol, reason=str(exc))
            else:
                log_provider("server_selected", self.name, "profile_minutes", server=address,
                             symbol=symbol, rowCount=len(rows))
                return rows
        detail = f"：{last_error}" if last_error else ""
        raise ProviderUnavailable(f"easy_tdx MAC 历史分钟行情暂不可用{detail}") from last_error

    def _read(self, client, market, symbol, start, end, limit, deadline) -> tuple[Candle, ...]:
        offset = 0
        size = min(limit, PAGE_SIZE) if start is None and end is None else PAGE_SIZE
        oldest = None
        selected: list[Candle] = []
        for _ in range(MAX_PAGES):
            if monotonic() >= deadline:
                raise ProviderUnavailable("MAC 分钟行情分页超时")
            page = client.get_stock_kline(market, symbol, Period.MIN_1, start=offset, count=size, adjust=Adjust.NONE)
            if page.empty:
                if offset == 0:
                    raise ProviderUnavailable("MAC 接口未返回原生分钟 K 线")
                break

            rows = tuple(_normalize(row) for row in page.to_dict("records"))
            earliest = min(bar.timestamp for bar in rows)
            if oldest is not None and earliest >= oldest:
                raise ProviderUnavailable("MAC 分钟行情分页未向历史推进")
            oldest = earliest
            offset += len(rows)
            selected.extend(
                bar for bar in rows
                if (start is None or bar.timestamp >= start) and (end is None or bar.timestamp < end)
            )
            if len(selected) >= limit or (start is not None and oldest <= start) or len(rows) < size:
                break
        else:
            raise ProviderUnavailable("MAC 分钟行情超出分页上限")

        return tuple(sorted(selected, key=lambda bar: bar.timestamp)[-limit:])
