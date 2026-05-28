import asyncio
from typing import List
import akshare as ak
import pandas as pd
from typing import Optional
from pydantic import BaseModel
from model.sw_industry_index_model import SwIndustryIndexModel


async def get_sw_index_first_info() -> List[SwIndustryIndexModel]:
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
        SwIndustryIndexModel(
            sw_level=1,
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


async def get_sw_index_second_info() -> List[SwIndustryIndexModel]:
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
        SwIndustryIndexModel(
            sw_level=2,
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


async def get_sw_index_third_info() -> List[SwIndustryIndexModel]:
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
        SwIndustryIndexModel(
            sw_level=3,
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
