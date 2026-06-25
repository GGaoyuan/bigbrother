import asyncio
from typing import List, Optional

from mootdx.quotes import Quotes

from app.base.safe_value import safe_float, safe_str
from app.providers.model.tdx_data import TdxKlineBar, TdxQuote

# 标准市场行情客户端（直连通达信行情服务器，无需客户端/虚拟机）
_client = Quotes.factory(market="std")


def _round2(val: Optional[float]) -> Optional[float]:
    return round(val, 2) if val is not None else None


async def get_tdx_quotes(symbols: List[str]) -> List[TdxQuote]:
    """通达信实时行情快照。

    symbols: 6 位证券代码列表，如 ["000001", "600000"]。
    """
    df = await asyncio.to_thread(_client.quotes, symbol=symbols)
    if df is None or df.empty:
        return []
    rows: List[TdxQuote] = []
    for _, row in df.iterrows():
        price = safe_float(row.get("price"))
        last_close = safe_float(row.get("last_close"))
        change_pct = None
        if price is not None and last_close:
            change_pct = _round2((price - last_close) / last_close * 100)
        rows.append(
            TdxQuote(
                code=safe_str(row.get("code")),
                price=price,
                last_close=last_close,
                open=safe_float(row.get("open")),
                high=safe_float(row.get("high")),
                low=safe_float(row.get("low")),
                volume=safe_float(row.get("vol")),
                amount=safe_float(row.get("amount")),
                change_pct=change_pct,
            )
        )
    return rows


async def get_tdx_daily_kline(symbol: str, offset: int = 60) -> List[TdxKlineBar]:
    """通达信日线 K 线。

    symbol: 6 位证券代码，如 "600000"。
    offset: 返回最近多少根日线。
    """
    # frequency=9 为日线
    df = await asyncio.to_thread(
        _client.bars, symbol=symbol, frequency=9, offset=offset
    )
    if df is None or df.empty:
        return []
    bars: List[TdxKlineBar] = []
    for _, row in df.iterrows():
        raw_dt = row.get("datetime")
        trade_date = str(raw_dt)[:10] if raw_dt is not None else None
        bars.append(
            TdxKlineBar(
                code=symbol,
                trade_date=trade_date,
                open=safe_float(row.get("open")),
                high=safe_float(row.get("high")),
                low=safe_float(row.get("low")),
                close=safe_float(row.get("close")),
                volume=safe_float(row.get("vol")),
                amount=safe_float(row.get("amount")),
            )
        )
    return bars
