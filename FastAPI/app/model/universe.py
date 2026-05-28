from typing import Optional

from pydantic import BaseModel


class Universe(BaseModel):

    # 证券代码（个股，如 "000001"）
    stock_code: Optional[str] = None

    # 证券名称（个股，如 "平安银行"）
    stock_name: Optional[str] = None


