import backtrader as bt
import numpy as np

#chatgpt版本
class RSRSIndicator(bt.Indicator):
    lines = ('rsrs',)
    params = (
        ('period', 14),  # 回归期数
        ('lookback', 14),  # 滚动窗口大小
    )

    def __init__(self, period=None, lookback=None):
        # 如果传入了 period 和 lookback 参数，则覆盖默认参数
        if period is not None:
            self.params.period = period
        if lookback is not None:
            self.params.lookback = lookback

        self.addminperiod(self.params.period + self.params.lookback)

    def next(self):
        prices = np.array(self.data.get(size=self.params.period))
        returns = np.diff(prices) / prices[:-1]
        X = np.arange(1, self.params.period)
        Y = returns

        # 线性回归
        slope, intercept = np.polyfit(X, Y, 1)
        rsrs = slope / np.std(Y)
        rsrs_mean = np.mean([rsrs for rsrs in self.lines.rsrs.get(size=self.params.lookback)])
        rsrs_std = np.std([rsrs for rsrs in self.lines.rsrs.get(size=self.params.lookback)])

        # 计算 RSRS 标准分
        rsrs_standard = (rsrs - rsrs_mean) / rsrs_std

        self.lines.rsrs[0] = rsrs_standard


# https://zhuanlan.zhihu.com/p/595970191
# 知乎版本

class RSRS(bt.Indicator):
    packages = (
        ('numpy', 'np'),
        ('statsmodels.api', 'sm'),
    )
    lines = ('rsrs', 'R2',)
    params = (('N', 18),)  # 回看N期

    def __init__(self):

        self.addminperiod(self.p.N)
        self.high = self.data.high  # 因变量
        self.low = self.data.low  # 自变量

    def next(self):
        high_N = self.high.get(ago=0, size=self.p.N)
        low_N = self.low.get(ago=0, size=self.p.N)

        try:
            low_N = sm.add_constant(np.array(low_N))
            model = sm.OLS(np.array(high_N), low_N)

            results = model.fit()
            self.lines.rsrs[0] = results.params[1]  # rsrs值,即斜率
            self.lines.R2[0] = results.rsquared  # R平方值

        except:
            print('except')
            self.lines.rsrs[0] = 0


class RSRS_Norm(bt.Indicator):
    lines = ('rsrs', 'R2', 'rsrs_norm', 'rsrs_norm_adjust', 'right',)
    params = (('N', 18),  # 计算回归系数(斜率)的回看期
              ('M', 600),)  # 计算rsrs均值的回看期

    def __init__(self):
        self.addminperiod(self.p.N)

        self.RSRS = RSRS(self.data, N=self.p.N)
        self.lines.rsrs = self.RSRS.rsrs  # 回归得到的斜率
        self.lines.R2 = self.RSRS.R2
        self.lines.rsrs_norm = (self.rsrs - bt.ind.Average(self.lines.rsrs,
                                                           period=self.p.M)) / bt.ind.StandardDeviation(self.lines.rsrs,
                                                                                                        period=self.p.M)  # rsrs标准分
        self.lines.rsrs_norm_adjust = self.lines.rsrs_norm * self.lines.R2  # rsrs修正标准分
        self.lines.right = self.lines.rsrs * self.lines.rsrs_norm_adjust  # rsrs右偏标准分