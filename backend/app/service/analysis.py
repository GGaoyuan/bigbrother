from typing import Dict

from app.service.capital import (
    get_dragon_tiger,
    get_margin_data,
    get_market_capital_flow,
    get_northbound_data,
)
from app.service.index_analysis import (
    get_core_index_analysis,
    get_index_spot,
    get_style_compare,
)
from app.service.industry import get_sw_industry
from app.service.bean import sanitize_json
from app.service.market_breadth import (
    get_fund_flow_rank,
    get_limit_pool_summary,
    get_market_volume_summary,
)
from app.service.news import get_news_overview
from app.service.sector import (
    get_realtime_sectors,
    get_sector_fund_flow,
    get_ths_sector_fund_flow,
)


async def get_market_analysis_dashboard() -> Dict[str, object]:
    """按 spec 汇总 A 股市场分析所需的全部核心数据。"""
    import asyncio

    (
        core_indices,
        index_spot,
        style_compare,
        volume_summary,
        limit_pools,
        fund_flow_rank,
        sectors,
        sector_flow,
        northbound,
        margin,
        dragon_tiger,
        market_flow,
        news_overview,
        sw_industry,
    ) = await asyncio.gather(
        get_core_index_analysis(),
        get_index_spot(),
        get_style_compare(),
        get_market_volume_summary(),
        get_limit_pool_summary(),
        get_fund_flow_rank("今日"),
        get_realtime_sectors(3),
        get_sector_fund_flow("今日", "行业资金流"),
        get_northbound_data(),
        get_margin_data(),
        get_dragon_tiger(),
        get_market_capital_flow(),
        get_news_overview(),
        get_sw_industry(),
        return_exceptions=True,
    )

    def _unwrap(result, default):
        return default if isinstance(result, Exception) else result

    ths_flow = {"ths_concept": [], "ths_industry": [], "error": "skipped_in_dashboard"}
    try:
        ths_flow = await get_ths_sector_fund_flow()
    except Exception:
        pass

    return sanitize_json({
        "index": {
            "core_daily": _unwrap(core_indices, {}),
            "spot": _unwrap(index_spot, []),
            "style_compare": _unwrap(style_compare, {}),
        },
        "breadth": {
            "volume": _unwrap(volume_summary, {}),
            "limit_pools": _unwrap(limit_pools, {}),
            "fund_flow_rank": _unwrap(fund_flow_rank, []),
        },
        "sector": {
            "realtime": _unwrap(sectors, {}),
            "industry_fund_flow": _unwrap(sector_flow, []),
            "ths_fund_flow": ths_flow,
            "sw_industry": _unwrap(sw_industry, {}),
        },
        "capital": {
            "northbound": _unwrap(northbound, {}),
            "margin": _unwrap(margin, {}),
            "dragon_tiger": _unwrap(dragon_tiger, []),
            "market_flow": _unwrap(market_flow, []),
        },
        "news": _unwrap(news_overview, {}),
    })
