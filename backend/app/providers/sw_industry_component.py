from typing import Optional
from pydantic import BaseModel
import asyncio
from typing import List

import akshare as ak
import pandas as pd


class SwIndustryComponent(BaseModel):
    # 证券代码（如 "000001"）
    stock_code: Optional[str] = None

    # 证券名称（如 "平安银行"）
    stock_name: Optional[str] = None

    # 申万最新权重
    sw_weight: Optional[float] = None

    # 申万计入日期（如 "2021-12-13"）
    sw_inclusion_date: Optional[str] = None



async def get_sw_index_component(symbol: str) -> List[SwIndustryComponent]:
    """
    获取申万行业成分股列表。

    参数:
        symbol: 行业代码（不含.SI后缀），如 "801010"

    映射: 证券代码 -> stock_code, 证券名称 -> stock_name,
         最新权重 -> sw_weight, 计入日期 -> sw_inclusion_date
    """
    df = await asyncio.to_thread(ak.index_component_sw, symbol)
    if df is None or df.empty:
        return []
    return [
        SwIndustryComponent(
            stock_code=row["证券代码"],
            stock_name=row["证券名称"],
            sw_weight=row.get("最新权重"),
            sw_inclusion_date=str(row["计入日期"]) if pd.notna(row.get("计入日期")) else None,
        )
        for _, row in df.iterrows()
    ]

