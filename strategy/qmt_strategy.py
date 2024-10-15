# encoding:gbk


"""
͵����������
"""
import datetime as dt
from logging import warning

import pandas as pd
""""""
def is_mainboard(stock_code: str) -> bool:
    """
    �Ƿ���������
    �Ͻ������壺600�� 601�� 603�� 605��ͷ
    ������壺000
    �����С�壺002
    Ŀǰ��С���Ѿ��������������
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

account = '800174' # �ڲ��Խ��׽�������ʱ��account��ֵ�ᱻ��ֵΪ���������е��˺ţ��༭����������ʱ����Ҫ�ֶ���ֵ��������������ִ�е��µ������������ʵ��ί��

def init(ContextInfo):
    print('init')

    # С��ָ������֤2000
    g.index1 = '399303.XSHE'
    # ����ָ������֤1000
    g.index2 = '000852.XSHG'
    # ָ���
    g.index_pool = [
        g.index1,
        g.index2,
    ]
    # �����ֶ�
    g.momentum_day = 144
    # ÿ������������С��ǿ���ж�(û����)
    g.j = 12
    g.w = 12
    # ��Ʊ�������Ȩ��
    g.factor_weights = [1, 1, 1, 1, 1]
    """�����ǲ�������"""
    # ��Ʊ����
    g.stock_num = 100
    # ÿ������ʱ�Ľ��ִ��������趨Ϊ3��
    g.buytimes = 3
    # ��λ
    g.position = 1 / g.buytimes
    # �����յ��쿪��ʱ�Ŀ����ʽ�
    g.cash = 0
    # �����յ��쿪��ʱ�����������Ĺ�Ʊ����
    g.position_count = 0
    # ��λ��(�����ʽ�/�ܹ��ʽ�)
    g.a = 0

    run_daily(prepare_stock_list, time='9:05', reference_security='000300.XSHG')
    run_daily(cash_check, time='9:05')  # ÿ���������ж�ÿ����������ʽ�
    run_daily(position_count, time='9:05')  # ÿ���������ж������������Ĺ�Ʊ����
    run_weekly()#����11.10�� 11.15�� 11.20����my_buy

    # ContextInfo.schedule_run(prepare_stockpool, '20231231235959', -1, dt.timedelta(days=1), 'prepare_stockpool')
    # prepare_stockpool(ContextInfo)
    ContextInfo.schedule_run(prepare_stockpool, '20231231094500', -1, dt.timedelta(minutes=1), 'ֹӯֹ��')

def handlebar(ContextInfo):
    pass


def daily_prepare(ContextInfo):
    """
    ÿ�տ���ǰ׼��,9:05׼ʱ����
    """
    #���жϽ����Ƿ���Խ���

    # ��ȡ�Ѿ����е��б�
    g.high_limit_list = []
    # δ�����
    print('prepare_stock_list')

    # �ж�ÿ�ο����ʽ�

    # �ж������������Ĺ�Ʊ����


def my_buy(ContextInfo):
    pass

def prepare_stockpool(ContextInfo):
    # ��ȡA�����й�Ʊ
    stock_list = ContextInfo.get_stock_list_in_sector('����A��')
    # ɸѡ���Խ��׵Ĺ�Ʊ
    tradable_stock_list = []
    for stock in stock_list:
        # ɸѡ���������С��Ĺ�Ʊ
        is_mainboard = bbutil.is_mainboard(stock)
        if not is_mainboard:
            continue
        # ��ȡ��Ʊ���ݣ�get_instrumentdetail�Ѿ����ڣ�Ҫ�滻��get_instrument_detail��
        stock_data = ContextInfo.get_instrument_detail(stock)
        # �޳�ST�Ĺ�Ʊ
        name = stock_data['InstrumentName']
        if 'ST' in name or '*' in name or '��' in name:
            continue
        # �޳����ɽ��׵Ĺ�Ʊ
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
	print('��ѯί�н����')
	for o in orders:
		print(
			f'��Ʊ����: {o.m_strInstrumentID}, �г�����: {o.m_strExchangeID}, ֤ȯ����: {o.m_strInstrumentName}, ��������: {o.m_nOffsetFlag}',
			f'ί������: {o.m_nVolumeTotalOriginal}, �ɽ�����: {o.m_dTradedPrice}, �ɽ�����: {o.m_nVolumeTraded}, �ɽ����:{o.m_dTradeAmount}')

	deals = get_trade_detail_data(account, 'stock', 'deal')
	print('��ѯ�ɽ������')
	for dt in deals:
		print(
			f'��Ʊ����: {dt.m_strInstrumentID}, �г�����: {dt.m_strExchangeID}, ֤ȯ����: {dt.m_strInstrumentName}, ��������: {dt.m_nOffsetFlag}',
			f'�ɽ��۸�: {dt.m_dPrice}, �ɽ�����: {dt.m_nVolume}, �ɽ����: {dt.m_dTradeAmount}')

	positions = get_trade_detail_data(account, 'stock', 'position')
	print('��ѯ�ֲֽ����')
	for dt in positions:
		print(
			f'��Ʊ����: {dt.m_strInstrumentID}, �г�����: {dt.m_strExchangeID}, ֤ȯ����: {dt.m_strInstrumentName}, �ֲ���: {dt.m_nVolume}, ��������: {dt.m_nCanUseVolume}',
			f'�ɱ���: {dt.m_dOpenPrice:.2f}, ��ֵ: {dt.m_dInstrumentValue:.2f}, �ֲֳɱ�: {dt.m_dPositionCost:.2f}, ӯ��: {dt.m_dPositionProfit:.2f}')

	accounts = get_trade_detail_data(account, 'stock', 'account')
	print('��ѯ�˺Ž����')
	for dt in accounts:
		print(f'���ʲ�: {dt.m_dBalance:.2f}, ���ʲ�: {dt.m_dAssureAsset:.2f}, ����ֵ: {dt.m_dInstrumentValue:.2f}',
			  f'�ܸ�ծ: {dt.m_dTotalDebit:.2f}, ���ý��: {dt.m_dAvailable:.2f}, ӯ��: {dt.m_dPositionProfit:.2f}')

	position_statistics = get_trade_detail_data(account, "FUTURE", 'POSITION_STATISTICS')
	for obj in position_statistics:
		if obj.m_nDirection == 49:
			continue
		PositionInfo_dict[obj.m_strInstrumentID + "." + obj.m_strExchangeID] = {
			"�ֲ�": obj.m_nPosition,
			"�ɱ�": obj.m_dPositionCost,
			"����ӯ��": obj.m_dFloatProfit,
			"��֤��ռ��": obj.m_dUsedMargin
		}
		print(PositionInfo_dict)

