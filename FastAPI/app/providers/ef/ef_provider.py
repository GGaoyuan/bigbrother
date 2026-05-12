import asyncio
import efinance as ef
from typing import List
from app.general.markettype_enum import MarketTypeEnum
from app.providers.ef.bean.realtime_quote_bean import RealtimeQuoteBean


def _safe_float(val) -> float:
    """安全转换为浮点数，处理 None 和 NaN"""
    try:
        v = float(val) if val is not None else 0.0
        return 0.0 if (v != v) else v
    except (ValueError, TypeError):
        return 0.0


async def get_realtime_quotes(market_type: MarketTypeEnum) -> List[RealtimeQuoteBean]:
    """
    获取指定市场类型的实时行情

    Args:
        market_type: 市场类型枚举

    Returns:
        实时行情列表
    """
    # 根据市场类型映射到 efinance 的 market 参数
    market_map = {
        MarketTypeEnum.HS_A_STOCK: "沪深A股",
        MarketTypeEnum.SH_A_STOCK: "沪A",
        MarketTypeEnum.SZ_A_STOCK: "深A",
        MarketTypeEnum.BJ_A_STOCK: "北A",
        MarketTypeEnum.CONVERTIBLE_BOND: "可转债",
        MarketTypeEnum.FUTURES: "期货",
        MarketTypeEnum.GEM: "创业板",
        MarketTypeEnum.US_STOCK: "美股",
        MarketTypeEnum.HK_STOCK: "港股",
        MarketTypeEnum.CHINA_CONCEPT: "中概股",
        MarketTypeEnum.NEW_STOCK: "新股",
        MarketTypeEnum.STAR_BOARD: "科创板",
        MarketTypeEnum.SH_CONNECT: "沪股通",
        MarketTypeEnum.SZ_CONNECT: "深股通",
        MarketTypeEnum.INDUSTRY_BOARD: "行业板块",
        MarketTypeEnum.CONCEPT_BOARD: "概念板块",
        MarketTypeEnum.HS_INDEX: "沪深系列指数",
        MarketTypeEnum.SH_INDEX: "上证系列指数",
        MarketTypeEnum.SZ_INDEX: "深证系列指数",
        MarketTypeEnum.ETF: "ETF",
        MarketTypeEnum.LOF: "LOF",
    }

    market_name = market_map.get(market_type)
    if not market_name:
        raise ValueError(f"不支持的市场类型: {market_type}")

    # 调用 efinance 获取实时行情
    df = await asyncio.to_thread(ef.stock.get_realtime_quotes, market_name)

    if df is None or df.empty:
        return []

    # 转换为 RealtimeQuoteBean 列表
    result = []
    for _, row in df.iterrows():
        result.append(RealtimeQuoteBean(
            code=str(row.get("股票代码", "")),
            name=str(row.get("股票名称", "")),
            price=_safe_float(row.get("最新价")),
            change=_safe_float(row.get("涨跌额")),
            change_pct=_safe_float(row.get("涨跌幅")),
            volume=_safe_float(row.get("成交量")),
            provider="efinance",
        ))

    return result
