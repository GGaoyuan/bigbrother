import asyncio

import akshare as ak
import pandas as pd


async def get_sw_index_first_info() -> pd.DataFrame:
    """
    获取申万一级行业指数信息。
    列：行业代码、行业名称、成份个数、静态市盈率、TTM(滚动)市盈率、市净率、静态股息率
    """
    df = await asyncio.to_thread(ak.sw_index_first_info)
    if df is None or df.empty:
        return pd.DataFrame()
    return df


async def get_sw_index_second_info() -> pd.DataFrame:
    """
    获取申万二级行业指数信息。
    列：行业代码、行业名称、上级行业、成份个数、静态市盈率、TTM(滚动)市盈率、市净率、静态股息率
    """
    df = await asyncio.to_thread(ak.sw_index_second_info)
    if df is None or df.empty:
        return pd.DataFrame()
    return df


async def get_sw_index_third_info() -> pd.DataFrame:
    """
    获取申万三级行业指数信息。
    列：行业代码、行业名称、上级行业、成份个数、静态市盈率、TTM(滚动)市盈率、市净率、静态股息率
    """
    df = await asyncio.to_thread(ak.sw_index_third_info)
    if df is None or df.empty:
        return pd.DataFrame()
    return df
