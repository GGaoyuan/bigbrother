import akshare as ak
from datetime import datetime, timedelta

def test():
    """
    可以通过调用 ak.stock_board_industry_name_ths() 查看同花顺的所有行业名称
    """
    industries = ak.stock_board_industry_name_ths()
    for column in industries.columns:
        print(industries[column])
    # 获取同花顺行业板块信息
    industry_board_df = ak.stock_board_industry_index_ths(symbol="元件", start_date="20241115", end_date="20241119")
    print(industry_board_df.columns)
    print(industry_board_df[['日期', '成交量', '成交额']])

class HeatMap:
    def __init__(self):
        pass

    def test(self):
        delta = 13
        # 获取当前日期
        start_date = (datetime.now() - timedelta(delta * 3)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="600519", period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        if len(stock_zh_a_hist_df) > delta:
            stock_zh_a_hist_df = stock_zh_a_hist_df.tail(delta)
        print(stock_zh_a_hist_df[["日期", "股票代码", "涨跌幅"]])


if __name__ == '__main__':
    heat_map = HeatMap()
    heat_map.test()