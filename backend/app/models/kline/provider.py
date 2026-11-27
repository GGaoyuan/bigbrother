"""通过 easy_tdx MAC 行情读取 K 线。"""

from datetime import datetime
from importlib.metadata import version as package_version
from math import isfinite
from time import monotonic

from easy_tdx import MacClient, Market, Period
from easy_tdx.mac.enums import Adjust

from app.core.exceptions import ProviderUnavailable, UnsupportedMarketData
from app.core.market_connection import MAC_SERVERS, fetch_market_data
from app.core.market_time import CHINA, candle_span
from app.core.symbols import stock_exchange

from .model import Adjustment, Candle, Interval


MARKETS = {"SSE": Market.SH, "SZSE": Market.SZ, "BSE": Market.BJ}
PERIODS = {
    "day": Period.DAILY, "week": Period.WEEKLY, "month": Period.MONTHLY,
    "1m": Period.MIN_1, "5m": Period.MIN_5, "60m": Period.MIN_60,
}
ADJUSTMENTS = {"none": Adjust.NONE, "qfq": Adjust.QFQ}
PAGE_SIZE = 700
MAX_PAGES = 128
SHARE_QUANTUM = 100


def _normalize(row: dict, interval: Interval, adjust: Adjustment) -> Candle:
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
    # MAC 分钟线成交量按固定粒度发布，成交额留空。
    # 复权只改变价格，成交额沿用主站返回的原始金额。
    amount = None
    if interval != "1m" and volume and row.get("amount") is not None:
        candidate = float(row["amount"])
        if isfinite(candidate) and candidate > 0 and (
            adjust != "none" or low - 0.01 <= candidate / volume <= high + 0.01
        ):
            amount = candidate
    return Candle(timestamp, end, opening, high, low, close, volume, amount, "shares", volume, precision, adjust)


class KlineProvider:
    name = "easy-tdx"
    version = package_version("easy-tdx")

    def __init__(self, mac_servers: tuple[str, ...] = MAC_SERVERS):
        self._mac_servers = mac_servers

    @property
    def adjustment_version(self) -> str:
        # MAC K 线未返回复权版本，按北京时间日期隔离缓存。
        return f"{self.name}:{self.version}:qfq:{datetime.now(CHINA).date()}"

    def get_klines(
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]:
        if interval not in PERIODS or adjust not in ADJUSTMENTS:
            raise UnsupportedMarketData("MAC K 线不支持该周期或复权方式")
        exchange = stock_exchange(symbol)
        if exchange == "BSE":
            raise UnsupportedMarketData("MAC K 线尚未核验北交所证券")
        if limit < 1 or (start is not None and end is not None and start >= end):
            raise UnsupportedMarketData("MAC K 线区间或条数无效")

        return fetch_market_data(
            MacClient, self._mac_servers, "MAC K 线",
            lambda client, deadline: self._read_klines(
                client, int(MARKETS[exchange]), symbol, interval, adjust, start, end, limit, deadline,
            ),
        )

    def _read_klines(self, client, market, symbol, interval, adjust, start, end, limit, deadline) -> tuple[Candle, ...]:
        period = PERIODS[interval]
        offset = 0
        size = min(limit, PAGE_SIZE) if start is None and end is None else PAGE_SIZE
        oldest = None
        selected: list[Candle] = []
        for _ in range(MAX_PAGES):
            if monotonic() >= deadline:
                raise ProviderUnavailable("MAC K 线分页超时")
            page = client.get_stock_kline(market, symbol, period, start=offset, count=size, adjust=ADJUSTMENTS[adjust])
            if page.empty:
                if offset == 0:
                    raise ProviderUnavailable("MAC 接口未返回 K 线")
                break

            rows = tuple(_normalize(row, interval, adjust) for row in page.to_dict("records"))
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
