from typing import List
from pydantic import BaseModel

from app.model.capital_flow_model import CapitalFlowModel


class TodayCapitalFlowModel(BaseModel):
    """单只股票/板块今日的日内分钟级资金流入流出时序数据"""
    stock_code: str
    flows: List[CapitalFlowModel]

