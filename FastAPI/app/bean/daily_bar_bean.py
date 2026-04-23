from pydantic import BaseModel


class DailyBarBean(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    code: str
    provider: str
