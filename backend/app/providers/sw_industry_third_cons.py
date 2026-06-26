from typing import List, Optional
# DEPRECATED: 此文件使用 akshare/efinance/adata 数据源，已禁用，需要迁移到 easy_tdx/mootdx

from pydantic import BaseModel
from app.base.utils import to_float
import asyncio

import akshare as ak
import pandas as pd


class SwIndustryThirdCons(BaseModel):
    """
    申万三级行业成分股详细信息
    数据源: akshare ak.sw_index_third_cons（乐咕乐股）
    """

    # 股票代码（如 "000001"）
    stock_code: Optional[str] = None

    # 股票名称（如 "平安银行"）
    stock_name: Optional[str] = None

    # 纳入时间（如 "2021-12-13"）
    sw_inclusion_date: Optional[str] = None

    # 所属申万一级行业名称
    sw_industry_l1_name: Optional[str] = None

    # 所属申万二级行业名称
    sw_industry_l2_name: Optional[str] = None

    # 所属申万三级行业名称
    sw_industry_l3_name: Optional[str] = None

    # 当前价格
    price: Optional[float] = None

    # 静态市盈率
    pe_ratio: Optional[float] = None

    # TTM 市盈率
    pe_ratio_ttm: Optional[float] = None

    # 市净率
    pb_ratio: Optional[float] = None

    # 股息率（%）
    dividend_yield: Optional[float] = None

    # 市值
    market_cap: Optional[float] = None

    # 归母净利润同比增长（三季度末，%）
    net_profit_yoy_q3: Optional[float] = None

    # 归母净利润同比增长（二季度末，%）
    net_profit_yoy_q2: Optional[float] = None

    # 营业收入同比增长（三季度末，%）
    revenue_yoy_q3: Optional[float] = None

    # 营业收入同比增长（二季度末，%）
    revenue_yoy_q2: Optional[float] = None




async def get_sw_index_third_cons(symbol: str) -> List[SwIndustryThirdCons]:
    """
    获取申万三级行业成分股的详细信息（估值、市值、业绩同比等）。

    参数:
        symbol: 申万三级行业代码，需带 .SI 后缀，如 "850111.SI"

    映射:
        股票代码 -> stock_code, 股票简称 -> stock_name, 纳入时间 -> sw_inclusion_date,
        申万1级 -> sw_industry_l1_name, 申万2级 -> sw_industry_l2_name,
        申万3级 -> sw_industry_l3_name, 价格 -> price, 市盈率 -> pe_ratio,
        市盈率ttm -> pe_ratio_ttm, 市净率 -> pb_ratio, 股息率 -> dividend_yield,
        市值 -> market_cap,
        归母净利润同比增长(09-30) -> net_profit_yoy_q3,
        归母净利润同比增长(06-30) -> net_profit_yoy_q2,
        营业收入同比增长(09-30) -> revenue_yoy_q3,
        营业收入同比增长(06-30) -> revenue_yoy_q2
    """
    df = await asyncio.to_thread(ak.sw_index_third_cons, symbol)
    if df is None or df.empty:
        return []
    return [
        SwIndustryThirdCons(
            stock_code=str(row.get("股票代码")) if pd.notna(row.get("股票代码")) else None,
            stock_name=str(row.get("股票简称")) if pd.notna(row.get("股票简称")) else None,
            sw_inclusion_date=str(row.get("纳入时间")) if pd.notna(row.get("纳入时间")) else None,
            sw_industry_l1_name=row.get("申万1级"),
            sw_industry_l2_name=row.get("申万2级"),
            sw_industry_l3_name=row.get("申万3级"),
            price=to_float(row.get("价格")),
            pe_ratio=to_float(row.get("市盈率")),
            pe_ratio_ttm=to_float(row.get("市盈率ttm")),
            pb_ratio=to_float(row.get("市净率")),
            dividend_yield=to_float(row.get("股息率")),
            market_cap=to_float(row.get("市值")),
            net_profit_yoy_q3=to_float(row.get("归母净利润同比增长(09-30)")),
            net_profit_yoy_q2=to_float(row.get("归母净利润同比增长(06-30)")),
            revenue_yoy_q3=to_float(row.get("营业收入同比增长(09-30)")),
            revenue_yoy_q2=to_float(row.get("营业收入同比增长(06-30)")),
        )
        for _, row in df.iterrows()
    ]
