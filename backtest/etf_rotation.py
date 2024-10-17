"""
https://www.joinquant.com/view/community/detail/1b1aea4e33780bb81e2883e1ca0e0e69
【回顾3】ETF策略之核心资产轮动
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import math
import backtrader as bt
from qmtbt import QMTStore


class BuyCondition(bt.Indicator):
    def __init__(self):
        pass


class SellCondition(bt.Indicator):
    def __init__(self):
        pass

class Size(bt.Sizer):
    def __init__(self):
        pass

class ETFRotationStrategy(bt.Strategy):
    def __init__(self):
        pass

    def next(self):
        pass


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # 获取和设置数据
    store = QMTStore()

    # 设置策略
    cerebro.addstrategy(ETFRotationStrategy)
    # 设置初始资金
    cerebro.broker.setcash(10000)
    # 佣金
    cerebro.broker.setcommission(commission=0.001)
    # 开始回测
    print('组合期初资金: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('组合期末资金: %.2f' % cerebro.broker.getvalue())
    # 画图
    cerebro.plot()