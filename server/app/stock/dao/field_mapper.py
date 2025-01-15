from pandas import DataFrame

"""
股票
"""
# 股票名称
STOCK_NAME = 'stock_name'
# 股票代码
STOCK_CODE = 'stock_code'
"""
行业
"""
# 行业名称
INDUSTRY_NAME = 'industry_name'
# 行业代码
INDUSTRY_CODE = 'industry_code'
"""
概念
"""
# 概念名称
CONCEPT_NAME = 'concept_name'
# 概念代码
CONCEPT_CODE = 'concept_code'
"""
通用
"""
# 涨跌幅
CHANGE = 'change'
# 换手率
turnover_ratio = 'turnover_ratio'
# 最高价
highest_price = 'highest_price'
# 最低价
lowest_price = 'lowest_price'
# 开盘价
open_price = 'open_price'
# 收盘价
close_price = 'close_price'
# 最新价
latest_price = 'latest_price'
# 交易所
exchange = 'exchange'
# 成交额
volume = 'volume'
# 流通市值
circulating_market_cap = 'circulating_market_cap'
# 总市值
total_market_cap = 'total_market_cap'


def rename_fields(df: DataFrame, fields: list[str]) -> DataFrame:
    if df.empty or not fields:
        return df
    # 获取交集
    intersection = set(fields).intersection(set(df.columns))
    pairs = {}
    for field in intersection:
        match field:
            case '涨跌幅':
                pairs[field] = CHANGE
            case '最新价':
                pairs[field] = latest_price
            case '成交额':
                pairs[field] = volume
            case '流通市值':
                pairs[field] = circulating_market_cap
            case '总市值':
                pairs[field] = total_market_cap
            case '换手率':
                pairs[field] = turnover_ratio
            case '所属行业':
                pairs[field] = INDUSTRY_NAME
    df = df.rename(columns=pairs)
    return df