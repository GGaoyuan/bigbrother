import asyncio
import efinance as ef
from typing import List
from app.bean import TodayBillBean, RealtimeQuoteBean


def _safe_float(val) -> float:
    try:
        v = float(val) if val is not None else 0.0
        return 0.0 if (v != v) else v
    except (ValueError, TypeError):
        return 0.0


async def get_today_bill(code: str) -> List[TodayBillBean]:
    """获取单只股票日内分钟级单子流入流出数据"""
    df = await asyncio.to_thread(ef.stock.get_today_bill, code)
    if df is None or df.empty:
        return []
    result = []
    for _, row in df.iterrows():
        result.append(TodayBillBean(
            time=str(row.get("时间", "")),
            main_net_inflow=_safe_float(row.get("主力净流入")),
            small_net_inflow=_safe_float(row.get("小单净流入")),
            medium_net_inflow=_safe_float(row.get("中单净流入")),
            large_net_inflow=_safe_float(row.get("大单净流入")),
            super_large_net_inflow=_safe_float(row.get("超大单净流入")),
        ))
    return result


async def get_realtime_quotes(codes: list[str]) -> list[RealtimeQuoteBean]:
    """获取多只股票实时行情，拉全量后按 codes 过滤"""
    df = await asyncio.to_thread(ef.stock.get_realtime_quotes)
    if df is None or df.empty:
        return []
    df = df[df["股票代码"].isin(codes)]
    result = []
    for _, row in df.iterrows():
        result.append(RealtimeQuoteBean(
            code=str(row.get("股票代码", "")),
            name=str(row.get("股票名称", "")),
            price=_safe_float(row.get("最新价")),
            change=_safe_float(row.get("涨跌额")),
            change_pct=_safe_float(row.get("涨跌幅")),
            volume=_safe_float(row.get("成交量")),
        ))
    return result
