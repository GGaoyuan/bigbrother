import akshare as ak
"""
获取股票，板块的排行数据，如龙虎榜
"""
def get_leader_list(start_date: str, end_date: str):
    """
    获取龙虎榜的股票详情
    """
    stock_lhb_detail_em_df = ak.stock_lhb_detail_em(start_date = start_date, end_date = end_date)
    print(stock_lhb_detail_em_df)