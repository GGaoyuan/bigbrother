from typing import Optional
from pydantic import BaseModel
import asyncio
from typing import List
import akshare as ak
import pandas as pd


class SwIndustryIndex(BaseModel):
    # 申万行业级别
    sw_level: Optional[int] = None

    # 申万行业代码（如 "801010.SI"）
    sw_industry_code: Optional[str] = None

    # 申万行业名称（如 "农林牧渔"）
    sw_industry_name: Optional[str] = None

    # 申万上级行业名称（二三级行业所属的上级行业）
    sw_parent_industry: Optional[str] = None

    # 申万行业成份个数
    sw_component_count: Optional[int] = None

    # 静态市盈率
    pe_static: Optional[float] = None

    # TTM(滚动)市盈率
    pe_ttm: Optional[float] = None

    # 市净率
    pb: Optional[float] = None

    # 静态股息率
    dividend_yield: Optional[float] = None




async def get_sw_index_first_info() -> List[SwIndustryIndex]:
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
        SwIndustryIndex(
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


async def get_sw_index_second_info() -> List[SwIndustryIndex]:
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
        SwIndustryIndex(
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


async def get_sw_index_third_info() -> List[SwIndustryIndex]:
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
        SwIndustryIndex(
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


class SwIndexBar(BaseModel):
    # 交易日期（YYYY-MM-DD）
    trade_date: Optional[str] = None
    # 收盘点位
    close: Optional[float] = None
    # 成交额（亿元）
    turnover: Optional[float] = None


async def get_sw_index_hist(symbol: str, period: str = "day") -> List[SwIndexBar]:
    """
    获取申万行业/综合指数历史日线。

    symbol: 申万指数代码（不带 .SI 后缀），如 "801003"=申万A指，"801010"=农林牧渔。
    period: day / week / month。

    返回按日期升序排列的 (trade_date, close, turnover) 序列。
    """
    df = await asyncio.to_thread(ak.index_hist_sw, symbol=symbol, period=period)
    if df is None or df.empty:
        return []

    bars: List[SwIndexBar] = []
    for _, row in df.iterrows():
        raw_date = row.get("日期")
        trade_date = str(raw_date)[:10] if raw_date is not None else None
        bars.append(
            SwIndexBar(
                trade_date=trade_date,
                close=row.get("收盘"),
                turnover=row.get("成交额"),
            )
        )
    return bars
