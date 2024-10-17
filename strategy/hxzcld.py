import numpy as np
import pandas as pd
import math
import time

from pandas.core.interchange.dataframe_protocol import DataFrame

from account import Account
from xtquant import xtdata
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
"""
ETF动量轮动
"""
class G:
    # 轮动的ETF
    etf_pool = [
        '518880.SH',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（海外资产）
        '159915.SZ',  # 创业板100（成长股，科技股，中小盘）
        '510180.SH',  # 上证180（价值股，蓝筹股，中大盘）
    ]
    # 动量参考天数
    m_days = 25
g = G()
# 全局的一个account，从qmt中获取仓位，等账户信息
account = Account()


def init():
    download_history_data()
    trade()

def download_history_data():
    print('download_history_data')
    # 下载历史数据
    for etf in g.etf_pool:
        xtdata.download_history_data(etf, '1d')



# 交易
def trade():
    # ['time', 'open', 'high', 'low', 'close', 'volume', 'amount', 'settle', 'openInterest']
    etf_dict = xtdata.get_market_data_ex(field_list=['open', 'high', 'close'], stock_list = g.etf_pool, period='1d', count=g.m_days)
    score_list = []
    for etf_code, df in etf_dict.items():
        y = df['log'] = np.log(df.close)
        x = df['num'] = np.arange(df.log.size)
        slope, intercept = np.polyfit(x, y, 1)
        annualized_returns = math.pow(math.exp(slope), 250) - 1
        r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
        score = annualized_returns * r_squared
        score_list.append(score)
    print(score_list)

    df = pd.DataFrame(index=g.etf_pool, data={'score':score_list})
    df = df.sort_values(by='score', ascending=False)
    rank_list = list(df.index)
    print(df)

    # 获取动量最高的一只ETF
    target_num = 1
    target_list = rank_list[:target_num]
    # 卖出
    hold_list = list(context.portfolio.positions)
    for etf in hold_list:
        if etf not in target_list:
            order_target_value(etf, 0)
            print('卖出' + str(etf))
        else:
            print('继续持有' + str(etf))
    # 买入
    hold_list = list(context.portfolio.positions)
    if len(hold_list) < target_num:
        value = context.portfolio.available_cash / (target_num - len(hold_list))
        for etf in target_list:
            if context.portfolio.positions[etf].total_amount == 0:
                order_target_value(etf, value)
                print('买入' + str(etf))
