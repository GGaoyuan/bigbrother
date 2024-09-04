import time, os
import akshare as ak
from stock.files import filepath  as fp
import pandas as pd
_stock_code = '代码'
_stock_name = '名称'
_market_value = '总市值'

def stock_pool():
    # 沪深京A股
    # stock_list = pd.DataFrame()
    if not os.path.exists(fp.stock_list_csv):
        stock_list = ak.stock_zh_a_spot_em()
        stock_list.to_csv(fp.stock_list_csv)
    else:
        stock_list = pd.read_csv(fp.stock_list_csv, dtype={_stock_code: str})
    # 剔除非主板+中小板的股票
    mask_code_prefix = stock_list[_stock_code].str.startswith(('002', '003', '600', '601', '603', '000'))
    stock_list = stock_list.loc[mask_code_prefix]
    # 剔除退市股票
    mask_delisting = ~stock_list[_market_value].isna()
    stock_list = stock_list.loc[mask_delisting]
    # 剔除ST股票
    mask_st = ~stock_list[_stock_name].str.contains('ST', na=True)
    stock_list = stock_list.loc[mask_st]
    # 计算
    avarage = stock_list[_market_value].mean()
    median = stock_list[_market_value].median()
    print(f'总市值平均值 = {avarage}, 总市值中位数 = {median}')

    # 总市值排序从大到小排序，并获取第500个数据到1000个数据
    sorted_list = stock_list.sort_values(_market_value, ascending=False)
    sorted_list = sorted_list.iloc[499:1000]
    print('sort-------------------')
    print(sorted_list[[_stock_code, _stock_name, _market_value]])
    print('-------------------')
    #获取大于x，小于y的市值的票
    lower_bound = 700000000.0
    upper_bound = 30000000000.0
    filtered_df = stock_list[(stock_list[_market_value] > lower_bound) & (stock_list[_market_value] < upper_bound)]
    print('sort-------------------')
    print(filtered_df[[_stock_code, _stock_name, _market_value]])
    print('-------------------')
