from pydantic import BaseModel
from typing import Optional


class RealtimeQuoteBean(BaseModel):
    code: str
    name: Optional[str] = None
    price: float
    change: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[float] = None
    provider: str
