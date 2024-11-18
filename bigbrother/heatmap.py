import akshare as ak

def test():
    # 获取同花顺行业板块信息
    industry_board_df = ak.stock_board_industry_index_ths(symbol="元件", start_date="20241115", end_date="20241115")
    print(industry_board_df)
    pass





if __name__ == '__main__':
    test()
    pass