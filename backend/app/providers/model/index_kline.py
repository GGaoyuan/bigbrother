"""指数 K 线数据模型"""

from typing import Optional

from pydantic import BaseModel


class IndexKlineBar(BaseModel):
    """指数 K 线单根数据

    参数:
        trade_date: 交易日期（YYYY-MM-DD）
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        amount: 成交额
        change_pct: 涨跌幅（%）
    """

    trade_date: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
    change_pct: Optional[float] = None
