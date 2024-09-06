import stock.util.data_reader as dr

"""
https://www.joinquant.com/view/community/detail/69182b9cc15c3f8d4ecc5b0b7373312b?type=1
"""


"""
2.1.选股+纵向仓位管理模型的核心逻辑
选股的思路可以简化成一个股票池，具体标准为：
市净率>0
营业收入同比增长率>0
净利润同比增长率>0
经营活动产生的现金流量净额/经营活动净收益>1


5.2.因子构建核心逻辑
本次模型的选股标准为：
市净率>1
市盈率>0且< 1000（剔除妖股）
营业收入同比增长率>30
净利润同比增长率>50
经营活动产生的现金流量净额/经营活动净收益>10
"""

def stock_pool():
    list = dr.get_market_stocks(available=True)
    print(list.columns)
    print(list)
    # 市净率大于1
    list = list[list['市净率'] > 1]
    # 市盈率 > 0 且 < 1000（剔除妖股）
    list = list[list['市盈率-动态'] > 0]
    list = list[list['市盈率-动态'] < 1000]
    # 获取财务数据
    stock_codes = list['代码'].to_list
    financial_datas = dr.get_financial_datas(stock_codes=stock_codes)

    print(financial_datas)



stock_pool()