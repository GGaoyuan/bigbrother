"""涨跌停池 provider — easy_tdx 全市场快照筛选，不缓存。

数据源：通达信 Mac 行情协议（不经东财节点，稳定）
做法：拿全市场快照，按涨跌幅接近板块涨跌停阈值筛选
  - 主板(60/00): ±10%
  - 创业板(30)/科创板(68): ±20%
  - 北交所(8/4/92): ±30%
  - ST 股名称带 ST: ±5%（无法仅凭代码识别，用名称兜底）
不缓存（实时数据）
"""

import asyncio
from typing import List, Optional

from easy_tdx import Category
from pydantic import BaseModel

from app.cache import CacheTTL
from app.providers.client.easy_tdx_client import get_mac_client
from app.providers.base_provider import BaseProvider
from app.providers.cache_decorator import cached_json

# 判定封板的容差（涨跌幅与阈值差距在此范围内算封板）
_TOLERANCE = 0.3


class LimitStock(BaseModel):
    """涨停/跌停股票"""

    code: str
    name: str
    price: float  # 现价
    pre_close: float  # 昨收
    change_pct: float  # 涨跌幅
    turnover: Optional[float] = None  # 换手率
    amount: Optional[float] = None  # 成交额


def _limit_threshold(code: str, name: str) -> float:
    """根据代码和名称返回涨跌停阈值百分比"""
    if "ST" in name.upper():
        return 5.0
    if code.startswith(("30", "68")):  # 创业板/科创板
        return 20.0
    if code.startswith(("8", "4", "92")):  # 北交所
        return 30.0
    return 10.0  # 主板


def _fetch_all_quotes() -> list:
    """拿沪深全市场原始快照"""
    client = get_mac_client()
    rows = []
    for category in (Category.SH, Category.SZ):
        df = client.get_stock_quotes_list(category=category, count=10000)
        if df is None or df.empty:
            continue
        for _, row in df.iterrows():
            close = row.get("close")
            pre_close = row.get("pre_close")
            if not close or not pre_close:
                continue
            rows.append(
                {
                    "code": str(row.get("code", "")),
                    "name": str(row.get("name", "")),
                    "close": float(close),
                    "pre_close": float(pre_close),
                    "change_pct": round((close - pre_close) / pre_close * 100, 2),
                    "turnover": float(row["turnover"]) if row.get("turnover") is not None else None,
                    "amount": float(row["amount"]) if row.get("amount") is not None else None,
                }
            )
    return rows


def _to_limit_stock(r: dict) -> dict:
    return LimitStock(
        code=r["code"],
        name=r["name"],
        price=r["close"],
        pre_close=r["pre_close"],
        change_pct=r["change_pct"],
        turnover=r.get("turnover"),
        amount=r.get("amount"),
    ).model_dump()


class LimitUpPoolProvider(BaseProvider[List[dict]]):
    """涨停池数据源（全市场筛选涨停）"""

    async def _fetch(self) -> List[dict]:
        def _do():
            rows = _fetch_all_quotes()
            result = []
            for r in rows:
                # 排除新股/次新首日（名称带 N/C，无涨跌幅限制）
                if r["name"].startswith(("N", "C")):
                    continue
                threshold = _limit_threshold(r["code"], r["name"])
                # 封板区间：[阈值-容差, 阈值+容差]，上界排除异常值（如新股）
                if threshold - _TOLERANCE <= r["change_pct"] <= threshold + _TOLERANCE:
                    result.append(_to_limit_stock(r))
            result.sort(key=lambda x: x["change_pct"], reverse=True)
            return result

        return await asyncio.to_thread(_do)

    @cached_json(namespace="limit_pool", key="limit_up", ttl=CacheTTL.NONE)
    async def get(self) -> List[dict]:
        """获取涨停池（不缓存）"""
        return await self._fetch()


class LimitDownPoolProvider(BaseProvider[List[dict]]):
    """跌停池数据源（全市场筛选跌停）"""

    async def _fetch(self) -> List[dict]:
        def _do():
            rows = _fetch_all_quotes()
            result = []
            for r in rows:
                if r["name"].startswith(("N", "C")):
                    continue
                threshold = _limit_threshold(r["code"], r["name"])
                # 封板区间：[-(阈值+容差), -(阈值-容差)]
                if -(threshold + _TOLERANCE) <= r["change_pct"] <= -(threshold - _TOLERANCE):
                    result.append(_to_limit_stock(r))
            result.sort(key=lambda x: x["change_pct"])
            return result

        return await asyncio.to_thread(_do)

    @cached_json(namespace="limit_pool", key="limit_down", ttl=CacheTTL.NONE)
    async def get(self) -> List[dict]:
        """获取跌停池（不缓存）"""
        return await self._fetch()
