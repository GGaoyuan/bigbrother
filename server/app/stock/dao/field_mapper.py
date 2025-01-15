from pandas import DataFrame

"""
股票
"""
# 股票名称
stock_name = 'stock_name'
# 股票代码
stock_code = 'stock_code'
"""
行业
"""
# 行业名称
industry_name = 'industry_name'
# 行业代码
industry_code = 'industry_code'
"""
概念
"""
# 概念名称
concept_name = 'concept_name'
# 概念代码
concept_code = 'concept_code'
"""
通用
"""
# 涨跌幅
change = 'change'
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
    if len(fields) == 0:
        return df
    for field in fields:
        #找对于的英文字段
        new_field = ''
        match field:
            case '涨跌幅':
                new_field = change
            case '最新价':
                new_field = latest_price
            case '成交额':
                new_field = volume
            case '流通市值':
                new_field = circulating_market_cap
            case '总市值':
                new_field = total_market_cap
            case '换手率':
                new_field = turnover_ratio
            case '所属行业':
                new_field = industry_name
        # 排除瞎JB传的情况和找不到
        if len(new_field) and field in df.columns:
            df = df.rename(columns={field: new_field})
    return df