from typing import Dict

from app.service.market_breadth import get_market_volume_summary

__all__ = ["get_market_volume_summary"]


async def get_sw_industry(sw_industry_code: list[str] | None = None) -> Dict:
    """保留占位，成交量相关请使用 market_breadth.get_market_volume_summary"""
    return await get_market_volume_summary()
