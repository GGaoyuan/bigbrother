from enum import Enum

class Columns(Enum):
    # 索引
    INDEX = 'index'
    """
    行业板块
    """
    # 板块代码
    INDUSTRY_CODE = 'industry_code'
    # 板块名称
    INDUSTRY_NAME = 'industry_name'
    """
    股票
    """
    # 股票代码
    STOCK_CODE = 'stock_code'
    # 股票名称
    STOCK_NAME = 'stock_name'

