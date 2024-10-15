class ContextInfo(object):
    def __init__(self):
        # 可通过此属性设定回测开始 / 结束的时间, 以 % Y - %m - % d % H: % M: %S格式传入
        self.start = ''
        self.end = ''
        # 设定回测初始资金,支持读写，默认为 1000000
        self.capital: float = 1000000
        # 获取当前周期，即基本信息中设置的默认周期，只读，返回string，返回值见：
        # https://dict.thinktrader.net/innerApi/variable_convention.html?id=Oh2LVe#contextinfo-period-%E8%8E%B7%E5%8F%96%E5%BD%93%E5%89%8D%E5%91%A8%E6%9C%9F
        self.period = '1d'
        # 获取主图当前运行到的K线索引号，只读，索引号从0开始
        self.barpos: int = 0
    def run_time(self, funcName, period, startTime):
        """
        funcName：回调函数名
        period：重复调用的时间间隔,'5nSecond'表示每5秒运行1次回调函数,'5nDay'表示每5天运行一次回调函数,'500nMilliSecond'表示每500毫秒运行1次回调函数
        startTime：表示定时器第一次启动的时间,如果要定时器立刻启动,可以设置历史的时间
        """
        print('')

    def get_trading_dates(self, stockcode='', start_date='', end_date='', count='', period='1d'):
        print()
