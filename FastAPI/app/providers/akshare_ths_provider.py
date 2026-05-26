import asyncio
import akshare as ak
from typing import List
from app.providers.efinance_provider.bean.realtime_quote_bean import RealtimeQuoteBean


def _safe_float(val) -> float:
    """安全转换为浮点数，处理 None 和 NaN"""
    try:
        v = float(val) if val is not None else 0.0
        return 0.0 if (v != v) else v
    except (ValueError, TypeError):
        return 0.0


async def get_realtime_quotes() -> List[RealtimeQuoteBean]:
    """
    获取全市场实时行情，数据来源新浪

    Returns:
        实时行情列表
    """
    df = await asyncio.to_thread(ak.stock_zh_a_spot)

    if df is None or df.empty:
        return []

    result = []
    for _, row in df.iterrows():
        result.append(RealtimeQuoteBean(
            stock_code=str(row.get("代码", "")),
            stock_name=str(row.get("名称", "")),
            price=_safe_float(row.get("最新价")),
            change=_safe_float(row.get("涨跌额")),
            change_pct=_safe_float(row.get("涨跌幅")),
            volume=_safe_float(row.get("成交量")),
            provider="akshare",
        ))

    return result
