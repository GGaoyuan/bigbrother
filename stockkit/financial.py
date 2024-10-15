from xtquant import xtdata
from datetime import datetime, timedelta


def download_data(stock_list=[], date_delta=10, callback=None):
	"""
	下载数据
	"""
	if not stock_list:
		stock_list = xtdata.get_stock_list_in_sector('沪深A股')
	start_time = (datetime.now() - timedelta(days=date_delta)).strftime('%Y%m%d')
	xtdata.download_financial_data2(stock_list, start_time=start_time, callback=callback)

def get_data():
	pass

def pb_ratio():
	pass

def pe_ratio():
	pass
