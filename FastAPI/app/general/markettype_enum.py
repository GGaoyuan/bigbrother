from enum import IntEnum


class MarketTypeEnum(IntEnum):
    """市场类型枚举"""

    # A 股市场
    HS_A_STOCK = 1  # 沪深A股市场行情
    SH_A_STOCK = 2  # 沪市A股市场行情
    SZ_A_STOCK = 3  # 深市A股市场行情
    BJ_A_STOCK = 4  # 北证A股市场行情

    # 债券市场
    CONVERTIBLE_BOND = 5  # 沪深可转债市场行情

    # 期货市场
    FUTURES = 6  # 期货市场行情

    # 特殊板块
    GEM = 7  # 创业板市场行情
    STAR_BOARD = 8  # 科创板市场行情

    # 国际市场
    US_STOCK = 9  # 美股市场行情
    HK_STOCK = 10  # 港股市场行情
    CHINA_CONCEPT = 11  # 中国概念股市场行情

    # 新股
    NEW_STOCK = 12  # 沪深新股市场行情

    # 互联互通
    SH_CONNECT = 13  # 沪股通市场行情
    SZ_CONNECT = 14  # 深股通市场行情

    # 板块
    INDUSTRY_BOARD = 15  # 行业板块市场行情
    CONCEPT_BOARD = 16  # 概念板块市场行情

    # 指数
    HS_INDEX = 17  # 沪深系列指数市场行情
    SH_INDEX = 18  # 上证系列指数市场行情
    SZ_INDEX = 19  # 深证系列指数市场行情

    # 基金
    ETF = 20  # ETF 基金市场行情
    LOF = 21  # LOF 基金市场行情
