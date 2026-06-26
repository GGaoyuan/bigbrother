"""通达信数据模型"""

from typing import Optional
from pydantic import BaseModel


class TdxQuote(BaseModel):
    """通达信实时行情快照

    参数:
        code: 股票代码
        price: 现价
        last_close: 昨收
        open: 开盘价
        high: 最高价
        low: 最低价
        volume: 成交量
        amount: 成交额
        change_pct: 涨跌幅（%）
    """
    code: Optional[str] = None
    price: Optional[float] = None
    last_close: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
    change_pct: Optional[float] = None


class TdxKlineBar(BaseModel):
    """通达信 K 线数据

    参数:
        code: 股票代码
        trade_date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        amount: 成交额
    """
    code: str
    trade_date: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
