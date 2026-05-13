from pydantic import BaseModel
from app.providers.ef import ef_provider
from app.providers.ak import ak_provider
from app.general.markettype_enum import MarketTypeEnum
import asyncio

# 默认使用 efinance，akshare 作为备用
_ef = ef_provider
_ak = ak_provider


async def get_realtime_sectors(value: int):
    """
    获取板块实时行情

    Args:
        value: 板块类型，1=行业板块，2=概念板块，3=全部板块

    Returns:
        dict: 包含 industry 和 concept 的字典
    """
    # 并发获取行业和概念板块数据
    industry_task = ef_provider.get_realtime_quotes(MarketTypeEnum.INDUSTRY_BOARD)
    concept_task = ef_provider.get_realtime_quotes(MarketTypeEnum.CONCEPT_BOARD)

    industry_data, concept_data = await asyncio.gather(industry_task, concept_task)

    # 根据 value 返回对应的数据
    if value == 1:
        return {"industry": industry_data}
    elif value == 2:
        return {"concept": concept_data}
    else:
        return {"industry": industry_data, "concept": concept_data}

