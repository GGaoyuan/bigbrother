from typing import Union
import backtrader as bt
from backtrader.indicators import MACD
from datetime import datetime
import stock.data_wrapper as dw
class JackCuiStrategy(bt.Strategy):
    params = (
        ('fastlen', 12),  # 快速EMA的长度
        ('slowlen', 26),  # 慢速EMA的长度
        ('signallen', 9),  # 信号线的EMA长度
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.fastlen,  # 快速均线周期
            period_me2=self.params.slowlen,  # 慢速均线周期
            period_signal=self.params.signallen  # 信号线周期
        )
        # DIF: MACD line
        self.dif = self.macd.lines.macd
        # DEA: Signal line
        self.dea = self.macd.lines.signal
        # MACD Histogram: (DIF - DEA)
        # self.macd_hist = self.macd.lines.histo

    def next(self):
        # 打印DIF, DEA 和 MACD 直方图
        print(f"Date: {self.data.datetime.date(0)}")
        print(f"DIF (MACD Line): {self.dif[0]:.2f}")
        print(f"DEA (Signal Line): {self.dea[0]:.2f}")
        # print(f"MACD Histogram: {self.macd_hist[0]}")
        print('-' * 20)




cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname = dw.get_market(stock_code='600535'))
cerebro.adddata(data)
cerebro.addstrategy(JackCuiStrategy)
cerebro.run()
# cerebro.plotter().show()