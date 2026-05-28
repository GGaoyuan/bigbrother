from typing import Optional
from pydantic import BaseModel
class SwIndustryIndexModel(BaseModel):
    # 申万行业级别
    sw_level: Optional[int] = None

    # 申万行业代码（如 "801010.SI"）
    sw_industry_code: Optional[str] = None

    # 申万行业名称（如 "农林牧渔"）
    sw_industry_name: Optional[str] = None

    # 申万上级行业名称（二三级行业所属的上级行业）
    sw_parent_industry: Optional[str] = None

    # 申万行业成份个数
    sw_component_count: Optional[int] = None

    # 静态市盈率
    pe_static: Optional[float] = None

    # TTM(滚动)市盈率
    pe_ttm: Optional[float] = None

    # 市净率
    pb: Optional[float] = None

    # 静态股息率
    dividend_yield: Optional[float] = None
