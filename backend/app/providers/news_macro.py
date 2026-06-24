import asyncio
import json
from typing import Any, List, Optional

import akshare as ak
import pandas as pd
from pydantic import BaseModel

from app.providers.client.parsers import safe_float, safe_str


class NewsItem(BaseModel):
    title: Optional[str] = None
    publish_time: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None


class MacroIndicator(BaseModel):
    indicator_name: Optional[str] = None
    trade_date: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None


class OverseasQuote(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None


async def get_stock_news(symbol: str = "603777") -> List[NewsItem]:
    df = await asyncio.to_thread(ak.stock_news_em, symbol=symbol)
    if df is None or df.empty:
        return []
    return [
        NewsItem(
            title=safe_str(row.get("新闻标题")),
            publish_time=safe_str(row.get("发布时间")),
            source=safe_str(row.get("文章来源")),
            url=safe_str(row.get("新闻链接")),
            content=safe_str(row.get("新闻内容")),
        )
        for _, row in df.iterrows()
    ]


async def get_macro_market_operation() -> List[MacroIndicator]:
    """央行公开市场操作，akshare 当前提供 bank_financing 接口。"""
    df = await asyncio.to_thread(ak.macro_china_bank_financing)
    if df is None or df.empty:
        return []
    return [
        MacroIndicator(
            indicator_name=safe_str(row.get("操作方式") or row.get("项目") or row.get("品种")),
            trade_date=safe_str(row.get("日期") or row.get("时间")),
            value=safe_float(row.get("利率") or row.get("投放金额") or row.get("回笼金额")),
            unit=safe_str(row.get("单位")),
        )
        for _, row in df.iterrows()
    ]


async def get_macro_lpr() -> List[MacroIndicator]:
    df = await asyncio.to_thread(ak.macro_china_lpr)
    if df is None or df.empty:
        return []
    return [
        MacroIndicator(
            indicator_name=safe_str(row.get("品种") or "LPR"),
            trade_date=safe_str(row.get("日期") or row.get("时间")),
            value=safe_float(row.get("1年") or row.get("5年") or row.get("利率")),
            unit="%",
        )
        for _, row in df.iterrows()
    ]


async def get_us_index_quotes() -> List[OverseasQuote]:
    symbols = [".DJI", ".IXIC", ".INX"]
    rows: List[OverseasQuote] = []
    for symbol in symbols:
        df = await asyncio.to_thread(ak.index_us_stock_sina, symbol=symbol)
        if df is None or df.empty:
            continue
        latest = df.iloc[-1]
        rows.append(
            OverseasQuote(
                symbol=symbol,
                name=safe_str(latest.get("名称") or symbol),
                price=safe_float(latest.get("收盘") or latest.get("close")),
                change_pct=safe_float(latest.get("涨跌幅")),
            )
        )
    return rows


async def get_pywencai_hot_concepts(query: str = "今日涨停概念排行") -> List[dict]:
    try:
        import pywencai
    except ImportError:
        return []
    try:
        result = await asyncio.to_thread(pywencai.get, query=query)
    except Exception:
        return []
    if isinstance(result, pd.DataFrame):
        records = result.to_dict(orient="records")
    elif isinstance(result, list):
        records = result
    else:
        return []
    return json.loads(json.dumps(records, ensure_ascii=False, default=str))
