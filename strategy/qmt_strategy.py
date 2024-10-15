# encoding:gbk


"""
偷鸡摸狗策略
"""
import datetime as dt
from logging import warning

import pandas as pd
""""""
def is_mainboard(stock_code: str) -> bool:
    """
    是否属于主板
    上交所主板：600， 601， 603， 605开头
    深交所主板：000
    深交所中小板：002
    目前中小板已经并入深交所主板了
    """
    if stock_code.startswith('600') or \
        stock_code.startswith('601') or \
        stock_code.startswith('603') or \
        stock_code.startswith('605') or \
        stock_code.startswith('000') or \
        stock_code.startswith('002'):
        return True
    else:
        return False
""""""
class G(): pass
g = G()

account = '800174' # 在策略交易界面运行时，account的值会被赋值为策略配置中的账号，编辑器界面运行时，需要手动赋值；编译器环境里执行的下单函数不会产生实际委托

def init(ContextInfo):
    print('init')

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

    run_daily(prepare_stock_list, time='9:05', reference_security='000300.XSHG')
    run_daily(cash_check, time='9:05')  # 每个买入日判断每次买入可用资金
    run_daily(position_count, time='9:05')  # 每个买入日判断新满足条件的股票数量
    run_weekly()#周三11.10， 11.15， 11.20运行my_buy

    # ContextInfo.schedule_run(prepare_stockpool, '20231231235959', -1, dt.timedelta(days=1), 'prepare_stockpool')
    # prepare_stockpool(ContextInfo)
    ContextInfo.schedule_run(prepare_stockpool, '20231231094500', -1, dt.timedelta(minutes=1), '止盈止损')

def handlebar(ContextInfo):
    pass


def daily_prepare(ContextInfo):
    """
    每日开盘前准备,9:05准时调用
    """
    #先判断今天是否可以交易

    # 获取已经持有的列表
    g.high_limit_list = []
    # 未完待续
    print('prepare_stock_list')

    # 判断每次可用资金

    # 判断新满足条件的股票数量


def my_buy(ContextInfo):
    pass

def prepare_stockpool(ContextInfo):
    # 获取A股所有股票
    stock_list = ContextInfo.get_stock_list_in_sector('沪深A股')
    # 筛选可以交易的股票
    tradable_stock_list = []
    for stock in stock_list:
        # 筛选出主板和中小板的股票
        is_mainboard = bbutil.is_mainboard(stock)
        if not is_mainboard:
            continue
        # 获取股票数据（get_instrumentdetail已经过期，要替换成get_instrument_detail）
        stock_data = ContextInfo.get_instrument_detail(stock)
        # 剔除ST的股票
        name = stock_data['InstrumentName']
        if 'ST' in name or '*' in name or '退' in name:
            continue
        # 剔除不可交易的股票
        status = stock_data['InstrumentStatus']
        expire_date = stock_data['ExpireDate']
        if status > 0 or not (expire_date == 0 or expire_date == 99999999):
            continue
        print(stock_data)
        tradable_stock_list.append(stock)

        # pb = C.get_financial_data('', '')
        print(len(tradable_stock_list))

def handlebaraaa(ContextInfo):
	if not ContextInfo.is_last_bar():
		return

	orders = get_trade_detail_data(account, 'stock', 'order')
	print('查询委托结果：')
	for o in orders:
		print(
			f'股票代码: {o.m_strInstrumentID}, 市场类型: {o.m_strExchangeID}, 证券名称: {o.m_strInstrumentName}, 买卖方向: {o.m_nOffsetFlag}',
			f'委托数量: {o.m_nVolumeTotalOriginal}, 成交均价: {o.m_dTradedPrice}, 成交数量: {o.m_nVolumeTraded}, 成交金额:{o.m_dTradeAmount}')

	deals = get_trade_detail_data(account, 'stock', 'deal')
	print('查询成交结果：')
	for dt in deals:
		print(
			f'股票代码: {dt.m_strInstrumentID}, 市场类型: {dt.m_strExchangeID}, 证券名称: {dt.m_strInstrumentName}, 买卖方向: {dt.m_nOffsetFlag}',
			f'成交价格: {dt.m_dPrice}, 成交数量: {dt.m_nVolume}, 成交金额: {dt.m_dTradeAmount}')

	positions = get_trade_detail_data(account, 'stock', 'position')
	print('查询持仓结果：')
	for dt in positions:
		print(
			f'股票代码: {dt.m_strInstrumentID}, 市场类型: {dt.m_strExchangeID}, 证券名称: {dt.m_strInstrumentName}, 持仓量: {dt.m_nVolume}, 可用数量: {dt.m_nCanUseVolume}',
			f'成本价: {dt.m_dOpenPrice:.2f}, 市值: {dt.m_dInstrumentValue:.2f}, 持仓成本: {dt.m_dPositionCost:.2f}, 盈亏: {dt.m_dPositionProfit:.2f}')

	accounts = get_trade_detail_data(account, 'stock', 'account')
	print('查询账号结果：')
	for dt in accounts:
		print(f'总资产: {dt.m_dBalance:.2f}, 净资产: {dt.m_dAssureAsset:.2f}, 总市值: {dt.m_dInstrumentValue:.2f}',
			  f'总负债: {dt.m_dTotalDebit:.2f}, 可用金额: {dt.m_dAvailable:.2f}, 盈亏: {dt.m_dPositionProfit:.2f}')

	position_statistics = get_trade_detail_data(account, "FUTURE", 'POSITION_STATISTICS')
	for obj in position_statistics:
		if obj.m_nDirection == 49:
			continue
		PositionInfo_dict[obj.m_strInstrumentID + "." + obj.m_strExchangeID] = {
			"持仓": obj.m_nPosition,
			"成本": obj.m_dPositionCost,
			"浮动盈亏": obj.m_dFloatProfit,
			"保证金占用": obj.m_dUsedMargin
		}
		print(PositionInfo_dict)

