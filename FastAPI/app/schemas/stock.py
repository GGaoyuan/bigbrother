from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ProviderEnum(str, Enum):
    BAOSTOCK = "baostock"
    AKSHARE = "akshare"


class DailyBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    code: str
    provider: str


class RealtimeQuote(BaseModel):
    code: str
    name: Optional[str] = None
    price: float
    change: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[float] = None
    provider: str
