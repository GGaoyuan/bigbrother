from app.providers.ef import EFProvider
from app.providers.ak import AKProvider
from app.general.markettype_enum import MarketTypeEnum
from app.providers.ef import ef_provider
import asyncio

# 默认使用 efinance，akshare 作为备用
_ef = EFProvider()
_ak = AKProvider()


async def get_realtime_sectors(value: int):
    """
    获取板块实时行情

    Args:
        value: 板块类型，1=行业板块，2=概念板块，3=全部板块

    Returns:
        板块实时行情列表
    """
    # 1：行业，2：概念，3：全部
    if value == 1:
        market_types = [MarketTypeEnum.INDUSTRY_BOARD]
    elif value == 2:
        market_types = [MarketTypeEnum.CONCEPT_BOARD]
    else:
        market_types = [MarketTypeEnum.INDUSTRY_BOARD, MarketTypeEnum.CONCEPT_BOARD]

    # 并发获取多个市场类型的行情
    tasks = [ef_provider.get_realtime_quotes(market_type) for market_type in market_types]
    results = await asyncio.gather(*tasks)

    # 合并结果
    all_quotes = []
    for quotes in results:
        all_quotes.extend(quotes)

    return all_quotes

