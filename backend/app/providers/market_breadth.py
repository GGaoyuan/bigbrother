import asyncio
# DEPRECATED: 此文件使用 akshare/efinance/adata 数据源，已禁用，需要迁移到 easy_tdx/mootdx

from datetime import datetime
from typing import List, Optional

import akshare as ak
import pandas as pd
from pydantic import BaseModel

from app.base.safe_value import safe_float, safe_int, safe_str
from app.base.date_tool import recent_trade_dates


class MarketSummary(BaseModel):
    market: Optional[str] = None
    trade_date: Optional[str] = None
    total_turnover: Optional[float] = None
    total_volume: Optional[float] = None
    stock_count: Optional[int] = None
    up_count: Optional[int] = None
    down_count: Optional[int] = None
    flat_count: Optional[int] = None


class LimitPoolStock(BaseModel):
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None
    limit_up_count: Optional[int] = None
    turnover: Optional[float] = None
    reason: Optional[str] = None
    pool_type: Optional[str] = None


class FundFlowRank(BaseModel):
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None
    fund_net_inflow: Optional[float] = None
    indicator: Optional[str] = None


def _today() -> str:
    return datetime.now().strftime("%Y%m%d")


async def get_sse_summary() -> List[MarketSummary]:
    df = await asyncio.to_thread(ak.stock_sse_summary)
    if df is None or df.empty:
        return []
    return [
        MarketSummary(
            market="SSE",
            trade_date=safe_str(row.get("交易日") or row.get("项目")),
            total_turnover=safe_float(row.get("成交金额")),
            total_volume=safe_float(row.get("成交量")),
            stock_count=safe_int(row.get("上市公司数") or row.get("主板")),
        )
        for _, row in df.iterrows()
    ]


async def get_szse_summary(date: Optional[str] = None) -> List[MarketSummary]:
    candidates = [date] if date else recent_trade_dates()
    for trade_date in candidates:
        if not trade_date:
            continue
        try:
            df = await asyncio.to_thread(ak.stock_szse_summary, date=trade_date)
            if df is None or df.empty:
                continue
            return [
                MarketSummary(
                    market="SZSE",
                    trade_date=trade_date,
                    total_turnover=safe_float(row.get("成交金额")),
                    total_volume=safe_float(row.get("成交量")),
                    stock_count=safe_int(row.get("上市公司数")),
                )
                for _, row in df.iterrows()
            ]
        except Exception:
            continue
    return []


async def get_market_turnover_snapshot() -> dict:
    df = await asyncio.to_thread(ak.stock_zh_a_spot_em)
    if df is None or df.empty:
        return {"total_turnover": 0, "stock_count": 0}
    turnover_col = "成交额" if "成交额" in df.columns else None
    total = float(df[turnover_col].apply(pd.to_numeric, errors="coerce").fillna(0).sum()) if turnover_col else 0
    return {"total_turnover": total, "stock_count": len(df)}


async def _fetch_limit_pool(fetcher, pool_type: str, date: Optional[str] = None) -> List[LimitPoolStock]:
    candidates = [date] if date else recent_trade_dates()
    for trade_date in candidates:
        if not trade_date:
            continue
        try:
            df = await asyncio.to_thread(fetcher, date=trade_date)
            if df is None or df.empty:
                continue
            return [
                LimitPoolStock(
                    stock_code=safe_str(row.get("代码")),
                    stock_name=safe_str(row.get("名称")),
                    price=safe_float(row.get("最新价")),
                    change_pct=safe_float(row.get("涨跌幅")),
                    limit_up_count=safe_int(row.get("连板数")),
                    turnover=safe_float(row.get("成交额")),
                    reason=safe_str(row.get("涨停原因") or row.get("跌停原因")),
                    pool_type=pool_type,
                )
                for _, row in df.iterrows()
            ]
        except Exception:
            continue
    return []


async def get_limit_up_pool(date: Optional[str] = None) -> List[LimitPoolStock]:
    return await _fetch_limit_pool(ak.stock_zt_pool_em, "limit_up", date)


async def get_limit_down_pool(date: Optional[str] = None) -> List[LimitPoolStock]:
    return await _fetch_limit_pool(ak.stock_zt_pool_dtgc_em, "limit_down", date)


async def get_broken_limit_pool(date: Optional[str] = None) -> List[LimitPoolStock]:
    return await _fetch_limit_pool(ak.stock_zt_pool_zbgc_em, "broken_limit", date)


async def get_strong_pool(date: Optional[str] = None) -> List[LimitPoolStock]:
    return await _fetch_limit_pool(ak.stock_zt_pool_strong_em, "strong", date)


async def get_individual_fund_flow_rank(indicator: str = "今日") -> List[FundFlowRank]:
    df = await asyncio.to_thread(ak.stock_individual_fund_flow_rank, indicator=indicator)
    if df is None or df.empty:
        return []
    return [
        FundFlowRank(
            stock_code=safe_str(row.get("代码")),
            stock_name=safe_str(row.get("名称")),
            price=safe_float(row.get("最新价")),
            change_pct=safe_float(row.get("今日涨跌幅") or row.get("涨跌幅")),
            fund_net_inflow=safe_float(row.get("今日主力净流入-净额") or row.get("主力净流入-净额")),
            indicator=indicator,
        )
        for _, row in df.iterrows()
    ]
