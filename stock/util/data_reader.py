import akshare as ak
import pandas as pd
import stock.util.data_reader_util as util
import os
import concurrent.futures
import time
def get_market_stocks(available = False) -> pd.DataFrame:
    """
    获取当前市场上的所有票
    available为True的时候，只返回
    主板，中小板，不包含ST，市值为0的股票
    """
    date_str = util.today_str()
    if util.is_today_data():
        date_str = util.yesterday_str()
    file_path = util.file_path(date_str=date_str, file_name='market_stocks.csv')
    if not os.path.exists(file_path):
        print('没有找到当前市场上所有股票的文件，正在请求数据...')
        stock_list = ak.stock_zh_a_spot_em()
        stock_list.to_csv(file_path, index=False)    #index=False表示不要包含索引
    stock_list = pd.read_csv(file_path, dtype={'代码': str})
    if not available:
        return stock_list
    else:
        #开始筛选（筛选条件为：主板，中小板，不包含ST，市值为0）
        main_board = stock_list[stock_list['代码'].str.startswith(('600', '601', '603', '000'))]
        small_board = stock_list[stock_list['代码'].str.startswith('002')]
        available_stocks = pd.concat([main_board, small_board])
        # 去掉股票名称中包含 'ST'
        available_stocks = available_stocks[~available_stocks['名称'].str.contains('ST')]
        # 去掉市值是0的股票（退市的）
        available_stocks = available_stocks[available_stocks['总市值'] > 0]
        return available_stocks

def get_financial_data(stock_code, indicator = "按报告期") -> (str, pd.DataFrame):
    """
    获取股票的金融数据
    indicator="按报告期"; choice of {"按报告期", "按年度", "按单季度"}
    """
    try:
        financial_data = ak.stock_financial_abstract_ths(symbol=stock_code, indicator=indicator)
        print(f"股票代码 {stock_code} 请求成功")
        return stock_code, financial_data
    except Exception as e:
        print(f"股票代码 {stock_code} 请求失败: {e}")
        return stock_code, None

def get_financial_datas(stock_codes: list, max_workers = 10, indicator = "按报告期"):
    """
    获取股票的金融数据
    indicator="按报告期"; choice of {"按报告期", "按年度", "按单季度"}
    """
    # 记录开始时间
    start_time = time.time()

    # 使用 ThreadPoolExecutor 进行多线程并发请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交请求
        futures = {executor.submit(get_financial_data, code, indicator): code for code in stock_codes}

        # 获取所有请求的结果
        results = []
        for future in concurrent.futures.as_completed(futures):
            stock_code, result = future.result()
            results.append((stock_code, result))

    # 记录结束时间
    end_time = time.time()

    print(f"完成 {len(stock_codes)} 次请求，耗时：{end_time - start_time:.2f} 秒")
    return results

list = get_market_stocks()
print(list)