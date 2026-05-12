import asyncio
import efinance as ef
from typing import List
from app.bean import TodayBillBean, MarketSentimentBean, DailyBarBean, RealtimeQuoteBean
from app.providers.ef_provider import EFProvider
from app.providers.ak_provider import AKProvider

# 默认使用 efinance，akshare 作为备用
_ef = EFProvider()
_ak = AKProvider()


def _safe_float(val) -> float:
    try:
        v = float(val) if val is not None else 0.0
        return 0.0 if (v != v) else v
    except (ValueError, TypeError):
        return 0.0


async def get_today_bill(codes: List[str]) -> dict[str, List[TodayBillBean]]:
    """并发获取多只股票日内分钟级单子流入流出数据"""

    async def _fetch(code: str) -> List[TodayBillBean]:
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

    results = await asyncio.gather(*[_fetch(code) for code in codes])
    return {code: bills for code, bills in zip(codes, results)}


async def get_realtime_quotes(codes: List[str]) -> List[RealtimeQuoteBean]:
    """获取多只股票实时行情"""
    return await _ef.get_realtime_quotes(codes)


async def get_daily(code: str, start: str, end: str) -> List[DailyBarBean]:
    """获取日线数据，优先使用 efinance"""
    return await _ef.get_daily(code, start, end)


async def get_market_sentiment() -> MarketSentimentBean:
    """获取全市场情绪数据，优先使用 efinance"""
    return await _ef.get_market_sentiment()
