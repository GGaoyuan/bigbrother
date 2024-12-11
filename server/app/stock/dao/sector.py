import akshare as ak
from .__cacher__ import *
"""
获取关于行业/概念板块的数据
"""

def get_concept_list() -> list[dict]:
    """
    获取概念板块列表
    """
    df = ak.stock_board_concept_name_em()
    result = df.to_dict(orient='records')
    return result

def get_concept_member_list(name: str):
    """
    获取概念板块成分股
    """
    stock_board_concept_cons_em_df = ak.stock_board_concept_cons_em(symbol="车联网")
    print(stock_board_concept_cons_em_df)

def get_concept_history_daily_list(name: str, start_date: str, end_date: str):
    """
    获取行业板块的历史数据
    """
    cons_df = ak.stock_board_concept_hist_em(symbol=name, period='daily', start_date=start_date, end_date=end_date, adjust='qfq')
    return cons_df


def get_industry_list() -> list[dict]:
    """
    获取行业板块列表
    """
    df = ak.stock_board_industry_name_em()
    result = df.to_dict(orient='records')
    return result


def get_industry_member_list(name: str):
    """
    获取行业板块的成分股
    """
    stock_board_industry_cons_em_df = ak.stock_board_industry_cons_em(symbol="小金属")
    print(stock_board_industry_cons_em_df)

@cache(Level.HOUR3)
def get_industry_history_daily_list(name: str, start_date: str, end_date: str):
    """
    获取行业板块的历史数据
    """
    print('11111')
    cons_df = ak.stock_board_industry_hist_em(symbol=name, period='日k', start_date=start_date,
                                              end_date=end_date, adjust='qfq')
    print('22222')
    return cons_df