import numpy as np
import pandas as pd
import math
from account import Account
from xtquant import xtdata
"""
ETF动量轮动
"""
class G():
    # 轮动的ETF
    etf_pool = [
        '518880.XSHG',  # 黄金ETF（大宗商品）
        '513100.XSHG',  # 纳指100（海外资产）
        '159915.XSHE',  # 创业板100（成长股，科技股，中小盘）
        '510180.XSHG',  # 上证180（价值股，蓝筹股，中大盘）
    ]
    # 动量参考天数
    m_days = 25
g = G()

account = Account()

def init():
    # 轮动的ETF
    # g.etf_pool = [
    #     '518880.XSHG',  # 黄金ETF（大宗商品）
    #     '513100.XSHG',  # 纳指100（海外资产）
    #     '159915.XSHE',  # 创业板100（成长股，科技股，中小盘）
    #     '510180.XSHG',  # 上证180（价值股，蓝筹股，中大盘）
    # ]
    # # 动量参考天数
    # g.m_days = 25
    #每天早上跑trade
    pass


# 基于年化收益和判定系数打分的动量因子轮动 https://www.joinquant.com/post/26142
def get_rank():
    score_list = []
    etf_pool = g.etf_pool
    for etf in etf_pool:

        # 获取轮动天数的收盘价
        df = attribute_history(etf, g.m_days, '1d', ['close'])
        y = df['log'] = np.log(df.close)
        x = df['num'] = np.arange(df.log.size)
        slope, intercept = np.polyfit(x, y, 1)
        annualized_returns = math.pow(math.exp(slope), 250) - 1
        r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
        score = annualized_returns * r_squared
        score_list.append(score)
    df = pd.DataFrame(index=etf_pool, data={'score':score_list})
    df = df.sort_values(by='score', ascending=False)
    rank_list = list(df.index)
    print(df)
    #record是画图的意思
    # record(黄金 = round(df.loc['518880.XSHG'], 2))
    # record(纳指 = round(df.loc['513100.XSHG'], 2))
    # record(成长 = round(df.loc['159915.XSHE'], 2))
    # record(价值 = round(df.loc['510180.XSHG'], 2))
    return rank_list

# 交易
def trade(context):
    # 获取动量最高的一只ETF
    target_num = 1
    target_list = get_rank()[:target_num]
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