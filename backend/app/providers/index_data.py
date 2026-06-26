import asyncio
# DEPRECATED: 此文件使用 akshare/efinance/adata 数据源，已禁用，需要迁移到 easy_tdx/mootdx

from datetime import datetime, timedelta
from typing import List, Optional

import akshare as ak
import pandas as pd
from pydantic import BaseModel

from app.base.safe_value import safe_float, safe_str

CORE_INDICES = {
    "sh": ("000001", "上证指数"),
    "sz": ("399001", "深证成指"),
    "cyb": ("399006", "创业板指"),
}

STYLE_INDICES = {
    "hs300": ("000300", "沪深300"),
    "zz500": ("000905", "中证500"),
    "zz1000": ("000852", "中证1000"),
    "zz2000": ("932000", "中证2000"),
}


class IndexDailyBar(BaseModel):
    index_code: Optional[str] = None
    index_name: Optional[str] = None
    trade_date: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    turnover: Optional[float] = None
    change_pct: Optional[float] = None


class IndexSpotQuote(BaseModel):
    index_code: Optional[str] = None
    index_name: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None
    change_amount: Optional[float] = None
    volume: Optional[float] = None
    turnover: Optional[float] = None


def _default_start(days: int = 250) -> str:
    return (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")


def _today() -> str:
    return datetime.now().strftime("%Y%m%d")


def _parse_index_hist(df: pd.DataFrame, index_code: str, index_name: str) -> List[IndexDailyBar]:
    if df is None or df.empty:
        return []
    rows: List[IndexDailyBar] = []
    for _, row in df.iterrows():
        rows.append(
            IndexDailyBar(
                index_code=index_code,
                index_name=index_name,
                trade_date=safe_str(row.get("日期")),
                open=safe_float(row.get("开盘")),
                high=safe_float(row.get("最高")),
                low=safe_float(row.get("最低")),
                close=safe_float(row.get("收盘")),
                volume=safe_float(row.get("成交量")),
                turnover=safe_float(row.get("成交额")),
                change_pct=safe_float(row.get("涨跌幅")),
            )
        )
    return rows


async def get_index_daily_hist(
    symbol: str,
    index_name: str = "",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[IndexDailyBar]:
    start = start_date or _default_start()
    end = end_date or _today()
    df = await asyncio.to_thread(
        ak.index_zh_a_hist,
        symbol=symbol,
        period="daily",
        start_date=start,
        end_date=end,
    )
    return _parse_index_hist(df, symbol, index_name)


async def get_core_indices_daily() -> List[IndexDailyBar]:
    tasks = [
        get_index_daily_hist(code, name)
        for code, name in CORE_INDICES.values()
    ]
    grouped = await asyncio.gather(*tasks)
    return [item for group in grouped for item in group]


async def get_style_indices_daily() -> List[IndexDailyBar]:
    tasks = [
        get_index_daily_hist(code, name)
        for code, name in STYLE_INDICES.values()
    ]
    grouped = await asyncio.gather(*tasks)
    return [item for group in grouped for item in group]


async def get_index_spot_quotes() -> List[IndexSpotQuote]:
    df = await asyncio.to_thread(ak.stock_zh_index_spot_em, symbol="沪深重要指数")
    if df is None or df.empty:
        return []
    return [
        IndexSpotQuote(
            index_code=safe_str(row.get("代码")),
            index_name=safe_str(row.get("名称")),
            price=safe_float(row.get("最新价")),
            change_pct=safe_float(row.get("涨跌幅")),
            change_amount=safe_float(row.get("涨跌额")),
            volume=safe_float(row.get("成交量")),
            turnover=safe_float(row.get("成交额")),
        )
        for _, row in df.iterrows()
    ]
