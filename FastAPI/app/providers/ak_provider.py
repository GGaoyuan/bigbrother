import asyncio
from typing import List

import akshare as ak
import pandas as pd

from app.model.universe import Universe


async def get_sw_index_component(symbol: str) -> List[Universe]:
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
        Universe(
            stock_code=row["证券代码"],
            stock_name=row["证券名称"],
            sw_weight=row.get("最新权重"),
            sw_inclusion_date=str(row["计入日期"]) if pd.notna(row.get("计入日期")) else None,
        )
        for _, row in df.iterrows()
    ]


async def get_sw_index_first_info() -> List[Universe]:
    """
    获取申万一级行业指数信息。

    映射: 行业代码 -> sw_industry_code, 行业名称 -> sw_industry_name,
         成份个数 -> sw_component_count, 静态市盈率 -> pe_static,
         TTM(滚动)市盈率 -> pe_ttm, 市净率 -> pb, 静态股息率 -> dividend_yield
    """
    df = await asyncio.to_thread(ak.sw_index_first_info)
    if df is None or df.empty:
        return []
    return [
        Universe(
            sw_industry_code=row["行业代码"],
            sw_industry_name=row["行业名称"],
            sw_component_count=int(row["成份个数"]),
            pe_static=row["静态市盈率"],
            pe_ttm=row["TTM(滚动)市盈率"],
            pb=row["市净率"],
            dividend_yield=row["静态股息率"],
        )
        for _, row in df.iterrows()
    ]


async def get_sw_index_second_info() -> List[Universe]:
    """
    获取申万二级行业指数信息。

    映射: 行业代码 -> sw_industry_code, 行业名称 -> sw_industry_name,
         上级行业 -> sw_parent_industry, 成份个数 -> sw_component_count,
         静态市盈率 -> pe_static, TTM(滚动)市盈率 -> pe_ttm,
         市净率 -> pb, 静态股息率 -> dividend_yield
    """
    df = await asyncio.to_thread(ak.sw_index_second_info)
    if df is None or df.empty:
        return []
    return [
        Universe(
            sw_industry_code=row["行业代码"],
            sw_industry_name=row["行业名称"],
            sw_parent_industry=row.get("上级行业"),
            sw_component_count=int(row["成份个数"]),
            pe_static=row["静态市盈率"],
            pe_ttm=row["TTM(滚动)市盈率"],
            pb=row["市净率"],
            dividend_yield=row["静态股息率"],
        )
        for _, row in df.iterrows()
    ]


async def get_sw_index_third_info() -> List[Universe]:
    """
    获取申万三级行业指数信息。

    映射: 行业代码 -> sw_industry_code, 行业名称 -> sw_industry_name,
         上级行业 -> sw_parent_industry, 成份个数 -> sw_component_count,
         静态市盈率 -> pe_static, TTM(滚动)市盈率 -> pe_ttm,
         市净率 -> pb, 静态股息率 -> dividend_yield
    """
    df = await asyncio.to_thread(ak.sw_index_third_info)
    if df is None or df.empty:
        return []
    return [
        Universe(
            sw_industry_code=row["行业代码"],
            sw_industry_name=row["行业名称"],
            sw_parent_industry=row.get("上级行业"),
            sw_component_count=int(row["成份个数"]),
            pe_static=row["静态市盈率"],
            pe_ttm=row["TTM(滚动)市盈率"],
            pb=row["市净率"],
            dividend_yield=row["静态股息率"],
        )
        for _, row in df.iterrows()
    ]
