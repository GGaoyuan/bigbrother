import asyncio
import akshare as ak
import pandas as pd
from typing import List


async def get_concept_board_list() -> pd.DataFrame:
    """
    获取同花顺概念板块列表（名称+代码）。
    """
    df = await asyncio.to_thread(ak.stock_board_concept_name_ths)
    if df is None or df.empty:
        return pd.DataFrame()
    return df


async def get_industry_board_list() -> pd.DataFrame:
    """
    获取同花顺行业板块列表（名称+代码）。
    """
    df = await asyncio.to_thread(ak.stock_board_industry_name_ths)
    if df is None or df.empty:
        return pd.DataFrame()
    return df