from typing import Optional

from pydantic import BaseModel


class Universe(BaseModel):

    # 证券代码（个股，如 "000001"）
    stock_code: Optional[str] = None

    # 证券名称（个股，如 "平安银行"）
    stock_name: Optional[str] = None

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

    # 个股在申万行业中的权重
    sw_weight: Optional[float] = None

    # 个股纳入申万行业的日期
    sw_inclusion_date: Optional[str] = None
