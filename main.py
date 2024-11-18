#from strategy import tjmg, hxzcld
# from xtquant import xtdata
from jqdatasdk import *
from xtquant import xtdata


def financial_download_data_callback(data):
    print(data)


if __name__ == '__main__':
    #xtdata.download_financial_data2(['600740.SH'], start_time='20201230', callback=None)
    #get_financial_data(stock_list, table_list=[], start_time='', end_time='', report_type='report_time')
    # data = xtdata.get_financial_data([])
    #print(data)
    #financial.download_data(date_delta=10, callback=financial_download_data_callback)
    # tjmg.init()
    # feishu.send_msg('1231232131\n,asdasdasdasdasdad')
    # account.test()
    """
    获取基金数据
    ret_sector_data = xtdata.get_stock_list_in_sector('沪深基金')
    print(ret_sector_data)
    instrument = xtdata.get_instrument_detail('510180.SH')
    print(instrument)
    """
    #hxzcld.init()
    stocks = xtdata.get_stock_list()
    df = jqdata.get_fundamentals(query(
        valuation.code,
        valuation.turnover_ratio,
        valuation.market_cap,
        valuation.circulating_market_cap
    ).filter(
        valuation.code.in_(stocks),
        # balance.total_liability / balance.total_assets < 0.8,#资产负债率<80%
        valuation.pb_ratio > 1,
        valuation.pe_ratio > 0,
        valuation.pe_ratio < 200,  # 市净率>0
        # indicator.inc_return > 2,#净资产收益率>0
        indicator.inc_total_revenue_year_on_year > 30,  # 营业总收入同比增长率
        # indicator.inc_total_revenue_annual > 30,    #营业总收入环比增长率
        indicator.inc_net_profit_year_on_year > 50,  # 净利润同比增长率
        # indicator.inc_net_profit_annual > 50,#净利润环比增长率
        indicator.ocf_to_operating_profit > 10,  # 经营活动产生的现金流量净额/经营活动净收益>5

    ).order_by(
        valuation.circulating_market_cap.asc()
        # valuation.market_cap.asc()#市值由小到大排列
    ))