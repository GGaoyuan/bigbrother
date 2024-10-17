from strategy import tjmg, hxzcld
from xtquant import xtdata
import yaml
def financial_download_data_callback(data):
    print(data)


if __name__ == '__main__':
    #xtdata.download_financial_data2(['600740.SH'], start_time='20201230', callback=None)
    #get_financial_data(stock_list, table_list=[], start_time='', end_time='', report_type='report_time')
    # data = xtdata.get_financial_data([])
    #print(data)
    #financial.download_data(date_delta=10, callback=financial_download_data_callback)
    # tjmg.init()

    """
    获取基金数据
    ret_sector_data = xtdata.get_stock_list_in_sector('沪深基金')
    print(ret_sector_data)
    instrument = xtdata.get_instrument_detail('510180.SH')
    print(instrument)
    """
    hxzcld.init()