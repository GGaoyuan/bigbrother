from typing import Optional
from pydantic import BaseModel


class SwIndustryComponentModel(BaseModel):
    # 证券代码（如 "000001"）
    stock_code: Optional[str] = None

    # 证券名称（如 "平安银行"）
    stock_name: Optional[str] = None

    # 申万最新权重
    sw_weight: Optional[float] = None

    # 申万计入日期（如 "2021-12-13"）
    sw_inclusion_date: Optional[str] = None
