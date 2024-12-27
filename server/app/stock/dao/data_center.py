import akshare as ak

"""
东方财富网-数据中心
"""
def get_daily_statistics(start_date: str, end_date: str):
    """
    机构买卖每日统计
    东方财富网-数据中心-龙虎榜单-机构买卖每日统计
    """
    stock_lhb_jgmmtj_em_df = ak.stock_lhb_jgmmtj_em(start_date=start_date, end_date=end_date)
    return stock_lhb_jgmmtj_em_df


def get_trading_seats(duration: str):
    """
    机构席位追踪
    东方财富网-数据中心-龙虎榜单-机构席位追踪
    """
    stock_lhb_jgstatistic_em_df = ak.stock_lhb_jgstatistic_em(symbol=duration)
    print(stock_lhb_jgstatistic_em_df)