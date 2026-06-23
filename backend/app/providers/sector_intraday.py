"""板块日内资金流——离线板块表 + efinance today_bill 并发聚合。

数据策略（唯一稳定可用方案）：
1. 静态 JSON 维护 50+ 热门概念板块代码+名称（sector_codes.json）
2. 运行时并发调 ef.stock.get_today_bill(code)，取每个板块的分时曲线
3. 最后一个点 = 最新净流入 → 排序得排行榜
4. 并发池控制（15 并发），避免过载

Why not 其他接口：
- efinance/akshare 东财板块排行：间歇性 Connection aborted
- 同花顺：py_mini_racer 在 macOS 崩溃
- 新浪/腾讯/网易：无板块资金流接口
- mootdx 协议：无资金流字段
- 唯一稳定：efinance.get_today_bill（单板块分时），从未失败
"""

import asyncio
import json
from pathlib import Path
from typing import List

import efinance as ef
from pydantic import BaseModel

_SECTOR_CODES_PATH = Path(__file__).parent / "sector_codes.json"
_CONCURRENCY = 15  # 并发数，过高可能被限流


class SectorSnapshot(BaseModel):
    """板块即时快照"""

    code: str
    name: str
    net_inflow: float  # 主力净流入（亿元）


class IntradayPoint(BaseModel):
    """日内分时点位"""

    time: str  # HH:MM
    net_inflow: float  # 截至该分钟的累计主力净流入（亿元）


class SectorIntraday(BaseModel):
    """单个板块的日内分时资金流"""

    code: str
    name: str
    points: List[IntradayPoint]


def _load_sector_codes() -> List[dict]:
    """加载静态板块代码表"""
    with open(_SECTOR_CODES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


async def _fetch_one_today_bill(code: str, name: str, sem: asyncio.Semaphore) -> SectorIntraday:
    """单个板块 today_bill，带并发控制"""
    async with sem:

        def _fetch():
            try:
                df = ef.stock.get_today_bill(code)
                if df.empty:
                    return SectorIntraday(code=code, name=name, points=[])
                pts = [
                    IntradayPoint(
                        time=row["时间"].split(" ")[1] if " " in row["时间"] else row["时间"],
                        net_inflow=float(row["主力净流入"] or 0) / 1e8,
                    )
                    for _, row in df.iterrows()
                    if "时间" in row and "主力净流入" in row
                ]
                return SectorIntraday(code=code, name=name, points=pts)
            except Exception:
                # 单个板块失败不影响其他，返回空
                return SectorIntraday(code=code, name=name, points=[])

        return await asyncio.to_thread(_fetch)


async def get_all_sectors_intraday() -> List[SectorIntraday]:
    """并发获取所有板块的日内分时（离线表 + today_bill）"""
    codes = _load_sector_codes()
    sem = asyncio.Semaphore(_CONCURRENCY)
    tasks = [_fetch_one_today_bill(s["code"], s["name"], sem) for s in codes]
    return await asyncio.gather(*tasks)


async def get_concept_boards_snapshot() -> List[SectorSnapshot]:
    """概念板块快照（从 today_bill 最后一个点推算）"""
    trends = await get_all_sectors_intraday()
    snapshots = []
    for t in trends:
        net = t.points[-1].net_inflow if t.points else 0.0
        snapshots.append(SectorSnapshot(code=t.code, name=t.name, net_inflow=net))
    return snapshots


async def get_sector_intraday(code: str) -> SectorIntraday:
    """单个板块的日内逐分钟（兼容旧接口）"""
    # 从静态表找名称
    codes = _load_sector_codes()
    name = next((s["name"] for s in codes if s["code"] == code), "")
    sem = asyncio.Semaphore(1)
    return await _fetch_one_today_bill(code, name, sem)
