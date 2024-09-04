import akshare as ak
import adata
import pandas as pd
# from stock.util.file import *
import stock.util.file as f
import os

def market_stocks() -> pd.DataFrame:
    """
    获取市场上的所有票
    """
    csv_path = f.get_file_path(f.market_stock_csv)
    if not os.path.exists(csv_path):
        stock_list = ak.stock_zh_a_spot_em()
        stock_list.to_csv(csv_path, index=False)    #index=False表示不要包含索引
    stock_list = pd.read_csv(csv_path, dtype={'代码': str})
    return stock_list

def market_available_stocks() -> pd.DataFrame:
    """
    筛选可交易的股票
    """
    stock_list = market_stocks()
    csv_path = f.get_file_path(f.market_tradable_stock_csv)
    if not os.path.exists(csv_path):
        # 只交易主板和中小板的股票
        print(stock_list['代码'].dtypes)
        main_board = stock_list[stock_list['代码'].startswith(('600', '601', '603', '000'))]
        small_board = stock_list[stock_list['代码'].startswith('002')]
        tradable_stocks = pd.concat([main_board, small_board])
        # 去掉股票名称中包含 'ST'
        tradable_stocks = tradable_stocks[~tradable_stocks['名称'].str.contains('ST')]
        # 去掉市值是0的股票（退市的）
        tradable_stocks = tradable_stocks[tradable_stocks['总市值'] > 0]
        tradable_stocks.to_csv(csv_path, index=False)
    else:
        tradable_stocks = pd.read_csv(csv_path)
    return tradable_stocks

stock_list = market_stocks()
main_board = stock_list[stock_list['代码'].str.startswith(('600', '601', '603', '000'))]
small_board = stock_list[stock_list['代码'].str.startswith('002')]
tradable_stocks = pd.concat([main_board, small_board])
for index, row in tradable_stocks.iterrows():
    print(row['代码'] + " + " + row['名称'])
# print(stock_list)
# for stock in stock_list:
#     print(stock['代码', '名称'])
# print(stock_list[['代码', '名称']])
# print(stock_list.dtypes)


# main_board = df[df['代码'].startswith(('600', '601', '603', '000'))]
# small_board = df[df['代码'].startswith('002')]
# tradable_stocks = pd.concat([main_board, small_board])
# print(tradable_stocks[['代码', '名称']])
# df = market_available_stocks()
# print(df[['代码', '名称']])
#
# query_result = df.loc[df['名称'] == '领益智造']
#
# # 显示查询结果
# print(query_result)

