"""
东方财富-行情中心
"""
import akshare as ak
import pandas as pd

def get_limit_up_data(date_str: str) -> pd.DataFrame:
    """
    东方财富网-行情中心-涨停板行情-涨停股池
    """
    stock_zt_pool_em_df = ak.stock_zt_pool_em(date=date_str)
    return stock_zt_pool_em_df


def get_limit_down_data(date_str: str) -> pd.DataFrame:
    """
    东方财富网-行情中心-涨停板行情-跌停股池
    """
    stock_zt_pool_dtgc_em_df = ak.stock_zt_pool_dtgc_em(date=date_str)
    return stock_zt_pool_dtgc_em_df

def get_industry_sector_data() -> pd.DataFrame:
    """
    东方财富网-行情中心-沪深京板块-行业板块
    """
    stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
    return stock_board_industry_name_em_df
