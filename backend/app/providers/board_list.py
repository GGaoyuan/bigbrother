"""板块列表 provider — easy_tdx MacClient，DAILY 缓存。

数据源：通达信 Mac 行情协议（不经东财节点，稳定）
缓存：1 天（板块列表变化慢）
"""

import asyncio
from typing import List, Optional

from easy_tdx import BoardType
from pydantic import BaseModel

from app.cache import CacheTTL
from app.providers.client.easy_tdx_client import get_mac_client
from app.providers.base_provider import BaseProvider
from app.providers.cache_decorator import cached_json


class BoardItem(BaseModel):
    """板块条目"""

    code: str  # 通达信板块代码，如 880656
    name: str
    price: Optional[float] = None  # 板块指数最新价
    pre_close: Optional[float] = None  # 昨收
    change_pct: Optional[float] = None  # 涨跌幅（自算）
    leader_code: Optional[str] = None  # 领涨股代码
    leader_name: Optional[str] = None  # 领涨股名称


# 板块类型字符串 -> easy_tdx BoardType 枚举
_BOARD_TYPE_MAP = {
    "concept": BoardType.GN,  # 概念
    "industry": BoardType.HY,  # 行业
    "region": BoardType.DQ,  # 地区
    "style": BoardType.FG,  # 风格
    "all": BoardType.ALL,
}


class BoardListProvider(BaseProvider[List[dict]]):
    """板块列表数据源

    参数:
        board_type: concept(概念) / industry(行业) / region(地区) / style(风格) / all
    """

    def __init__(self, board_type: str = "concept"):
        self.board_type = board_type

    async def _fetch(self) -> List[dict]:
        """从 easy_tdx 获取板块列表"""

        def _do():
            client = get_mac_client()
            bt = _BOARD_TYPE_MAP.get(self.board_type, BoardType.GN)
            df = client.get_board_list(board_type=bt)
            if df is None or df.empty:
                return []
            items = []
            for _, row in df.iterrows():
                price = row.get("price")
                pre_close = row.get("pre_close")
                change_pct = None
                if price is not None and pre_close:
                    change_pct = round((price - pre_close) / pre_close * 100, 2)
                items.append(
                    BoardItem(
                        code=str(row.get("code", "")),
                        name=str(row.get("name", "")),
                        price=float(price) if price is not None else None,
                        pre_close=float(pre_close) if pre_close is not None else None,
                        change_pct=change_pct,
                        leader_code=str(row.get("symbol_code", "")) or None,
                        leader_name=str(row.get("symbol_name", "")) or None,
                    )
                )
            return [it.model_dump() for it in items]

        return await asyncio.to_thread(_do)

    @cached_json(namespace="board_list", key="board_{board_type}", ttl=CacheTTL.DAILY)
    async def get(self) -> List[dict]:
        """获取板块列表（DAILY 缓存）"""
        return await self._fetch()
