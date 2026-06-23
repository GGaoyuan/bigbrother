from typing import Dict, List, Optional

from app.cache import CacheTTL
from app.providers.board_data import (
    get_sector_fund_flow_hist,
    get_sector_fund_flow_rank,
)
from app.service.bean import tag_datasource
from app.service.fetch import with_json_cache


async def get_sector_flow_ranking(
    indicator: str = "今日",
    sector_type: str = "行业资金流",
) -> Dict[str, List[dict]]:
    """
    今日板块资金流入/流出排行。

    返回 { inflow: [...], outflow: [...], all: [...] }：
      - inflow：主力净流入 > 0，按净流入降序
      - outflow：主力净流入 < 0，按净流入升序（流出最多在前）
      - all：全部板块，按名称用于右侧 A~Z 列表
    DAILY 缓存。
    """
    cache_key = f"sector_flow_rank_{indicator}_{sector_type}"

    async def _fetch():
        items = await get_sector_fund_flow_rank(indicator, sector_type)
        rows = [
            {
                "sector_name": it.sector_name,
                "change_pct": it.change_pct,
                "fund_net_inflow": it.fund_net_inflow,
            }
            for it in items
            if it.sector_name
        ]
        tagged = tag_datasource(rows, "EAST_MONEY")

        inflow = sorted(
            [r for r in tagged if (r.get("fund_net_inflow") or 0) > 0],
            key=lambda r: r["fund_net_inflow"],
            reverse=True,
        )
        outflow = sorted(
            [r for r in tagged if (r.get("fund_net_inflow") or 0) < 0],
            key=lambda r: r["fund_net_inflow"],
        )
        # 右侧列表按名称 A~Z（拼音/字符）排序
        all_sorted = sorted(tagged, key=lambda r: (r.get("sector_name") or ""))

        return {"inflow": inflow, "outflow": outflow, "all": all_sorted}

    return await with_json_cache(cache_key, CacheTTL.DAILY, _fetch)


async def get_sector_flow_trend(sector_name: str) -> Dict[str, object]:
    """
    单个板块的资金流历史走势，用于图表叠加。
    按板块名称分别 DAILY 缓存。

    返回 { sector_name, points: [{ time, value }] }，
    value 为主力净流入净额（元）。
    """
    safe_name = sector_name.strip()
    cache_key = f"sector_flow_trend_{safe_name}"

    async def _fetch():
        bars = await get_sector_fund_flow_hist(safe_name)
        points = [
            {"time": b.trade_date, "value": b.main_net_inflow}
            for b in bars
            if b.trade_date and b.main_net_inflow is not None
        ]
        return {"sector_name": safe_name, "points": points}

    return await with_json_cache(cache_key, CacheTTL.DAILY, _fetch)
