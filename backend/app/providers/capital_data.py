import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

import akshare as ak
from pydantic import BaseModel

from app.base.safe_value import safe_float, safe_str
from app.base.date_tool import recent_trade_dates


class NorthboundFlow(BaseModel):
    trade_date: Optional[str] = None
    net_inflow: Optional[float] = None
    buy_amount: Optional[float] = None
    sell_amount: Optional[float] = None
    symbol: Optional[str] = None


class MarginBalance(BaseModel):
    trade_date: Optional[str] = None
    market: Optional[str] = None
    margin_balance: Optional[float] = None
    short_balance: Optional[float] = None
    total_balance: Optional[float] = None


class DragonTigerEntry(BaseModel):
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    trade_date: Optional[str] = None
    close_price: Optional[float] = None
    change_pct: Optional[float] = None
    net_buy: Optional[float] = None
    buy_amount: Optional[float] = None
    sell_amount: Optional[float] = None
    reason: Optional[str] = None


class MarketFundFlow(BaseModel):
    trade_date: Optional[str] = None
    main_net_inflow: Optional[float] = None
    super_large_net_inflow: Optional[float] = None
    large_net_inflow: Optional[float] = None
    medium_net_inflow: Optional[float] = None
    small_net_inflow: Optional[float] = None


def _today() -> str:
    return datetime.now().strftime("%Y%m%d")


def _default_start(days: int = 180) -> str:
    return (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")


async def get_northbound_summary() -> List[NorthboundFlow]:
    df = await asyncio.to_thread(ak.stock_hsgt_fund_flow_summary_em)
    if df is None or df.empty:
        return []
    return [
        NorthboundFlow(
            trade_date=safe_str(row.get("交易日")),
            net_inflow=safe_float(row.get("资金净流入") or row.get("成交净买额")),
            buy_amount=safe_float(row.get("买入成交额")),
            sell_amount=safe_float(row.get("卖出成交额")),
            symbol=safe_str(row.get("类型") or row.get("板块")),
        )
        for _, row in df.iterrows()
    ]


async def get_northbound_hist(symbol: str = "北向资金") -> List[NorthboundFlow]:
    df = await asyncio.to_thread(ak.stock_hsgt_hist_em, symbol=symbol)
    if df is None or df.empty:
        return []
    return [
        NorthboundFlow(
            trade_date=safe_str(row.get("日期")),
            net_inflow=safe_float(row.get("当日成交净买额") or row.get("当日资金流入")),
            symbol=symbol,
        )
        for _, row in df.iterrows()
    ]


async def get_margin_sse(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[MarginBalance]:
    start = start_date or _default_start()
    end = end_date or _today()
    df = await asyncio.to_thread(ak.stock_margin_sse, start_date=start, end_date=end)
    if df is None or df.empty:
        return []
    return [
        MarginBalance(
            trade_date=safe_str(row.get("信用交易日期") or row.get("日期")),
            market="SSE",
            margin_balance=safe_float(row.get("融资余额")),
            short_balance=safe_float(row.get("融券余额")),
            total_balance=safe_float(row.get("融资融券余额")),
        )
        for _, row in df.iterrows()
    ]


async def get_margin_szse(date: Optional[str] = None) -> List[MarginBalance]:
    candidates = [date] if date else recent_trade_dates()
    last_error: Exception | None = None
    for trade_date in candidates:
        if not trade_date:
            continue
        try:
            df = await asyncio.to_thread(ak.stock_margin_szse, date=trade_date)
            if df is None or df.empty:
                continue
            return [
                MarginBalance(
                    trade_date=trade_date,
                    market="SZSE",
                    margin_balance=safe_float(row.get("融资余额")),
                    short_balance=safe_float(row.get("融券余额")),
                    total_balance=safe_float(row.get("融资融券余额")),
                )
                for _, row in df.iterrows()
            ]
        except Exception as exc:
            last_error = exc
            continue
    if last_error:
        raise last_error
    return []


async def get_dragon_tiger_list(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[DragonTigerEntry]:
    start = start_date or _today()
    end = end_date or _today()
    df = await asyncio.to_thread(ak.stock_lhb_detail_em, start_date=start, end_date=end)
    if df is None or df.empty:
        return []
    return [
        DragonTigerEntry(
            stock_code=safe_str(row.get("代码")),
            stock_name=safe_str(row.get("名称")),
            trade_date=safe_str(row.get("上榜日")),
            close_price=safe_float(row.get("收盘价")),
            change_pct=safe_float(row.get("涨跌幅")),
            net_buy=safe_float(row.get("龙虎榜净买额")),
            buy_amount=safe_float(row.get("龙虎榜买入额")),
            sell_amount=safe_float(row.get("龙虎榜卖出额")),
            reason=safe_str(row.get("上榜原因")),
        )
        for _, row in df.iterrows()
    ]


async def get_market_fund_flow() -> List[MarketFundFlow]:
    df = await asyncio.to_thread(ak.stock_market_fund_flow)
    if df is None or df.empty:
        return []
    return [
        MarketFundFlow(
            trade_date=safe_str(row.get("日期")),
            main_net_inflow=safe_float(row.get("主力净流入-净额")),
            super_large_net_inflow=safe_float(row.get("超大单净流入-净额")),
            large_net_inflow=safe_float(row.get("大单净流入-净额")),
            medium_net_inflow=safe_float(row.get("中单净流入-净额")),
            small_net_inflow=safe_float(row.get("小单净流入-净额")),
        )
        for _, row in df.iterrows()
    ]
