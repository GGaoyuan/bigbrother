from typing import Optional

from pydantic import BaseModel


class TdxQuote(BaseModel):
    # 通达信实时行情快照
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
    # 通达信日线 K 线
    code: Optional[str] = None
    trade_date: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
