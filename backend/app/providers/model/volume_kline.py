"""成交量分布（筹码分布）K 线数据模型"""

from typing import Optional

from pydantic import BaseModel


class VolumeKlineBar(BaseModel):
    """成交量分布所用的 K 线单根数据

    参数:
        datetime: K 线时间（日线 YYYY-MM-DD，分钟线 YYYY-MM-DD HH:MM）
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量（手）
        amount: 成交额（元）
    """

    datetime: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
