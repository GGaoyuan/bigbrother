from datetime import datetime
from pydantic import BaseModel
from app.base.datasource_from import DatasourceFrom
class CapitalFlowModel(BaseModel):
    """
    股票资金流入流出数据模型
    包含：股票代码、时间、主力净流入、小单/中单/大单/超大单净流入
    """
    # 股票代码
    stock_code: str
    # 时间
    time: datetime
    # 主力净流入
    main_net_inflow: float
    # 小单净流入
    small_order_inflow: float
    # 中单净流入
    medium_order_inflow: float
    # 大单净流入
    large_order_inflow: float
    # 超大单净流入
    extra_large_order_inflow: float
    # 数据源
    datasource: DatasourceFrom