import akshare as ak
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pandas import DataFrame, Series

class IndustryDao:
    def __init__(self):
        pass

    def get_industries_hist_daily(self):
        def get_industry_hist(industry: tuple):
            series = industry[1]
            industry_name = series['板块名称']
            try:
                delta = 13
                # 获取当前日期
                start_date = (datetime.now() - timedelta(delta * 3)).strftime('%Y%m%d')
                end_date = datetime.now().strftime('%Y%m%d')
                cons_df = ak.stock_board_industry_hist_em(symbol=industry_name, period='日k', start_date=start_date,
                                           end_date=end_date, adjust='qfq')
                return cons_df
            except Exception as e:
                print(f"{industry_name} 数据获取失败: {e}")


        # 先获取列表
        industry_list = ak.stock_board_industry_name_em()
        # industry_name_list = industry_list['板块名称']
        # print(len(industry_list))
        with ThreadPoolExecutor(max_workers=len(industry_list)) as executor:
            results = executor.map(get_industry_hist, industry_list.iterrows())
        for result in results:
            print(result)
