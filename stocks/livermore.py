from enum import Enum
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from datas import datafile
import os


n_pct = 6
s_pct = 3

class Node:
    def __init__(self, value):
        self.last_node: Node = None
        self.next_node: Node = None
        self.price = None
        self.datetime = None

class Peroid:
    class Grid(Enum):
        SECONDARY_RALLY = 1     # 次级回升
        NATURAL_RALLY = 2       # 自然回升
        UPWARD_TREND = 3        # 上升趋势
        DOWNWARD_TREND = 4      # 下降趋势
        NATURAL_Reaction = 5    # 自然回撤
        SECONDARY_Reaction = 6  # 次级回撤
    def __init__(self):
        self.last_peroid: Peroid = None
        self.next_peroid: Peroid = None


def feed(df: pd.DataFrame):
    print(df.columns)
    # df[['日期', '股票代码', '开盘', '收盘', '最高', '最低']]
    for index, row in df.iterrows():
        print(df.loc[index])


if __name__ == '__main__':
    # 获取当前日期
    end_date = datetime.today().strftime('%Y%m%d')
    # 计算开始日期为30天前
    start_date = (datetime.today() - timedelta(days=30)).strftime('%Y%m%d')

    market_stock_csv = 'stock.csv'
    file_path = datafile.file_path(market_stock_csv)
    if not os.path.exists(file_path):
        # 使用 AKShare 获取贵州茅台的股价数据
        stock_data = ak.stock_zh_a_hist(symbol="600519", period="daily", start_date=start_date, end_date=end_date,
                                        adjust="qfq")
        stock_data.to_csv(file_path)
    stock_data = pd.read_csv(file_path)

    # 查看结果
    feed(stock_data)