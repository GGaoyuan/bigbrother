from typing import Dict, List

from app.cache.sw_industry_cache import sw_industry_cache
from app.providers.akshare_lglg import (
    get_sw_index_first_info,
    get_sw_index_second_info,
    get_sw_index_third_info,
)


async def get_sw_industry() -> Dict[str, List[dict]]:
    """
    获取申万一二三级行业数据，带本地文件缓存（1天过期）。

    Returns:
        {"first": [...], "second": [...], "third": [...]}
    """
    # 读取缓存
    cached = await sw_industry_cache.get()
    if cached is not None:
        return cached

    # 请求申万一二三级行业数据
    df_first = await get_sw_index_first_info()
    df_second = await get_sw_index_second_info()
    df_third = await get_sw_index_third_info()

    data = {
        "first": df_first.to_dict(orient="records") if not df_first.empty else [],
        "second": df_second.to_dict(orient="records") if not df_second.empty else [],
        "third": df_third.to_dict(orient="records") if not df_third.empty else [],
    }

    # 写入缓存
    await sw_industry_cache.set(value=data)

    return data
