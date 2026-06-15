import asyncio
from typing import List, Optional

import akshare as ak
from pydantic import BaseModel

from app.providers.base.parsers import safe_float, safe_int, safe_str


class BoardQuote(BaseModel):
    board_name: Optional[str] = None
    board_type: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None
    turnover: Optional[float] = None
    turnover_rate: Optional[float] = None
    up_count: Optional[int] = None
    down_count: Optional[int] = None
    leader_stock: Optional[str] = None


class SectorFundFlow(BaseModel):
    sector_name: Optional[str] = None
    sector_type: Optional[str] = None
    change_pct: Optional[float] = None
    fund_net_inflow: Optional[float] = None
    indicator: Optional[str] = None


async def get_concept_board_quotes() -> List[BoardQuote]:
    df = await asyncio.to_thread(ak.stock_board_concept_name_em)
    if df is None or df.empty:
        return []
    return [
        BoardQuote(
            board_name=safe_str(row.get("板块名称")),
            board_type="concept",
            price=safe_float(row.get("最新价")),
            change_pct=safe_float(row.get("涨跌幅")),
            turnover=safe_float(row.get("成交额")),
            turnover_rate=safe_float(row.get("换手率")),
            up_count=safe_int(row.get("上涨家数")),
            down_count=safe_int(row.get("下跌家数")),
            leader_stock=safe_str(row.get("领涨股票")),
        )
        for _, row in df.iterrows()
    ]


async def get_industry_board_quotes() -> List[BoardQuote]:
    df = await asyncio.to_thread(ak.stock_board_industry_name_em)
    if df is None or df.empty:
        return []
    return [
        BoardQuote(
            board_name=safe_str(row.get("板块名称")),
            board_type="industry",
            price=safe_float(row.get("最新价")),
            change_pct=safe_float(row.get("涨跌幅")),
            turnover=safe_float(row.get("成交额")),
            turnover_rate=safe_float(row.get("换手率")),
            up_count=safe_int(row.get("上涨家数")),
            down_count=safe_int(row.get("下跌家数")),
            leader_stock=safe_str(row.get("领涨股票")),
        )
        for _, row in df.iterrows()
    ]


async def get_sector_fund_flow_rank(
    indicator: str = "今日",
    sector_type: str = "行业资金流",
) -> List[SectorFundFlow]:
    df = await asyncio.to_thread(
        ak.stock_sector_fund_flow_rank,
        indicator=indicator,
        sector_type=sector_type,
    )
    if df is None or df.empty:
        return []
    return [
        SectorFundFlow(
            sector_name=safe_str(row.get("名称")),
            sector_type=sector_type,
            change_pct=safe_float(row.get("今日涨跌幅") or row.get("涨跌幅")),
            fund_net_inflow=safe_float(row.get("今日主力净流入-净额") or row.get("主力净流入-净额")),
            indicator=indicator,
        )
        for _, row in df.iterrows()
    ]


async def get_ths_concept_fund_flow(symbol: str = "即时") -> List[SectorFundFlow]:
    df = await asyncio.to_thread(ak.stock_fund_flow_concept, symbol=symbol)
    if df is None or df.empty:
        return []
    return [
        SectorFundFlow(
            sector_name=safe_str(row.get("行业")),
            sector_type="ths_concept",
            change_pct=safe_float(row.get("行业-涨跌幅")),
            fund_net_inflow=safe_float(row.get("净额")),
            indicator=symbol,
        )
        for _, row in df.iterrows()
    ]


async def get_ths_industry_fund_flow(symbol: str = "即时") -> List[SectorFundFlow]:
    df = await asyncio.to_thread(ak.stock_fund_flow_industry, symbol=symbol)
    if df is None or df.empty:
        return []
    return [
        SectorFundFlow(
            sector_name=safe_str(row.get("行业")),
            sector_type="ths_industry",
            change_pct=safe_float(row.get("行业-涨跌幅")),
            fund_net_inflow=safe_float(row.get("净额")),
            indicator=symbol,
        )
        for _, row in df.iterrows()
    ]
