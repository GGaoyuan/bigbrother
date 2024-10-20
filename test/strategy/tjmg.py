from datetime import datetime, timedelta
from bigbrother import factors
# import talib
from xtquant import xtdata


class G(): pass
g = G()


def init():
    # g_prepare()
    # daily_prepare()
    my_trader()
    print("123123123123")


def g_prepare():
    """
    初始化对g对象的设置
    """
    print('g_prepare')
    # 小盘指数，国证2000
    g.index1 = '399303.XSHE'
    # 大盘指数，中证1000
    g.index2 = '000852.XSHG'
    # 指标池
    g.index_pool = [
        g.index1,
        g.index2,
    ]
    # 动量轮动
    g.momentum_day = 144
    # 每个季度做出大小盘强弱判断(没看懂)
    g.j = 12
    g.w = 12
    # 股票打分因子权重
    g.factor_weights = [1, 1, 1, 1, 1]
    """以下是策略设置"""
    # 股票数量
    g.stock_num = 100
    # 每次买入时的建仓次数，先设定为3次
    g.buytimes = 3
    # 仓位
    g.position = 1 / g.buytimes
    # 买入日当天开盘时的可用资金
    g.cash = 0
    # 买入日当天开盘时新满足条件的股票数量
    g.position_count = 0
    # 仓位率(已用资金/总共资金)
    g.a = 0


def daily_prepare(ContextInfo):
    """
    每日开盘前准备,9:05准时调用
    """
    # 先判断今天是否可以交易
    # 获取已经持有的列表
    g.high_limit_list = []
    # 未完待续
    print('prepare_stock_list')


# 判断每次可用资金
# 判断新满足条件的股票数量


def handlebar():
    pass


def my_buy():
    pass


def my_sell():
    pass


def my_trader():
    """
    获取选股列表，并过滤部分不合策略的股票
    """
    # 上一个交易日
    yesterday = ''
    # 当前交易日
    today = ''
    """
    过滤一些不符合要求的股票
    """
    # 获取所有的票
    stocks = xtdata.get_stock_list_in_sector('沪深A股')
    print(f"一共: {len(stocks)}支股票")
    base_filter_stocks = []
    # 过滤到只有主板，再剔除涨停跌停，停牌，退市的票
    for stock in stocks:
        # 判断是否是主板
        is_mainboard = factors.is_mainboard(stock)
        if not is_mainboard:
            continue
        # 获取股票的基础信息数据（该信息每交易日9点更新）
        instrument = xtdata.get_instrument_detail(stock)
        # 剔除退市，ST的股票
        name = instrument['InstrumentName']
        if 'ST' in name or '*' in name or '退' in name:
            # print(f"《{name}》是退市(ST)的票")
            continue
        # 剔除上市3个月内的票
        open_date = datetime.strptime(instrument['OpenDate'], "%Y%m%d")
        limit_date = datetime.now() - timedelta(days=390)
        if open_date > limit_date:
            # print(f"《{name}》是新股")
            continue
        # 停牌状态(<=0:正常交易（-1:复牌）;>=1停牌天数
        if instrument['InstrumentStatus'] > 0:
            # print(f"《{name}》有停牌")
            continue
        # ExpireDate为0 或 99999999 时，表示该标的暂无退市日或到期日
        if instrument['ExpireDate'] != 0 and instrument['ExpireDate'] != 99999999:
            # print(f"《{name}》有退市日或到期日")
            continue
        base_filter_stocks.append(stock)
    print(f"符合要求的股票一共: {len(base_filter_stocks)}支")
    """
    通过财务数据筛选出基本面还不错的公司
    """
    # todo
    financial_filter_stocks = ['600740.SH']
    """
    因子计算
    """
    # 计算单独因子值
    TO, CMC, PN, TV, RE = [], [], [], [], []
    for stock in financial_filter_stocks:
        pass
        # xtdata.get_turnove
        # xtdata.get_turnover_rate()
        # # 换手率
        # to = df.loc[stock]['turnover_ratio']
        # TO.append(to)
        # # 流通市值
        # cmc = df.loc[stock]['circulating_market_cap']
        # CMC.append(cmc)
        # # 当前价格
        # pricenow = get_close(stock, 1, '1m')
        # PN.append(pricenow)
        # # 21日累计成交量
        # total_volume_n = attribute_history(stock, 21, '1d', 'volume')['volume'].sum()
        # TV.append(total_volume_n)
        # # 55日涨幅
        # m_days_return = get_return(stock, 55, '1d')
        # RE.append(m_days_return)
