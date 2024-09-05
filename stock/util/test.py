import akshare as ak
import pandas as pd
import datetime, time
import stock.util.files as f
import os
from pathlib import Path
import concurrent.futures

def data_dir_path() -> str:
    # 提取文件名（不含扩展名）作为文件夹名
    current_dir = Path(__file__).parent.absolute()
    parent_dir = current_dir.parent
    datas_dir = os.path.join(parent_dir, 'data')
    return datas_dir

def market_stocks() -> pd.DataFrame:
    """
    获取当前市场上的所有票
    """
    cur_day = datetime.datetime.now()
    if cur_day.hour < 15:
        last_day = cur_day - datetime.timedelta(days=1)
        last_day_str = last_day.strftime('%Y-%m-%d')
        print(f'当前时间小于收盘的15点，将选用昨日{last_day_str}的数据')
    csv_path = f.get_scv_path(f.stock_list_all)
    if not os.path.exists(csv_path):
        print('没有找到当前市场上所有股票的文件，正在请求数据...')
        stock_list = ak.stock_zh_a_spot_em()
        stock_list.to_csv(csv_path, index=False)    #index=False表示不要包含索引
    stock_list = pd.read_csv(csv_path, dtype={'代码': str})
    return stock_list

market_stocks()

def market_available_stocks() -> pd.DataFrame:
    """
    筛选可交易的股票（主板，中小板，不包含ST，市值为0）
    """
    # stock_list = market_stocks()
    # main_board = stock_list[stock_list['代码'].str.startswith(('600', '601', '603', '000'))]
    # small_board = stock_list[stock_list['代码'].str.startswith('002')]
    # available_stocks = pd.concat([main_board, small_board])
    # # 去掉股票名称中包含 'ST'
    # available_stocks = available_stocks[~available_stocks['名称'].str.contains('ST')]
    # # 去掉市值是0的股票（退市的）
    # available_stocks = available_stocks[available_stocks['总市值'] > 0]
    # return available_stocks

#
# import akshare as ak
# import time
#
#
# # 获取 A 股股票的代码列表
# def get_stock_codes():
#     stock_data = ak.stock_zh_a_spot_em()  # 获取 A 股所有股票的实时数据
#     stock_codes = stock_data['代码'].tolist()  # 提取股票代码列
#     return stock_codes
#
#
# # 根据股票代码获取对应的财务数据
# def get_financial_data(stock_code):
#     try:
#         # 调用 ak.stock_financial_abstract_ths 接口获取财务摘要
#         financial_data = ak.stock_financial_abstract_ths(symbol=stock_code, indicator="按报告期")
#         print(f"股票代码 {stock_code} 请求成功")
#         return stock_code, financial_data
#     except Exception as e:
#         print(f"股票代码 {stock_code} 请求失败: {e}")
#         return stock_code, None
#
#
#
#
#
# # 多线程请求的主函数
# def fetch_financial_data_concurrently(stock_codes, max_workers=10):
#     # 记录开始时间
#     start_time = time.time()
#
#     # 使用 ThreadPoolExecutor 进行多线程并发请求
#     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#         # 提交请求
#         futures = {executor.submit(get_financial_data, code): code for code in stock_codes}
#
#         # 获取所有请求的结果
#         results = []
#         for future in concurrent.futures.as_completed(futures):
#             stock_code, result = future.result()
#             results.append((stock_code, result))
#
#     # 记录结束时间
#     end_time = time.time()
#
#     print(f"完成 {len(stock_codes)} 次请求，耗时：{end_time - start_time:.2f} 秒")
#     return results
#
#
# # 主程序入口
# if __name__ == "__main__":
#     # 第一步：获取所有 A 股股票代码
#     stock_codes = get_stock_codes()
#
#     # 可以选择限制请求的股票数量进行测试，如 stock_codes[:100]
#     # 第二步：并发获取所有股票的财务数据
#     financial_data = fetch_financial_data_concurrently(stock_codes, max_workers=10)
#
#     # 输出每个股票请求的结果（仅打印前 5 个）
#     for stock_code, data in financial_data[:5]:
#         print(f"股票代码 {stock_code} 的财务数据：")
#         if data is not None:
#             print(data.head())  # 打印财务数据的前几行
#         else:
#             print("请求失败或无数据")