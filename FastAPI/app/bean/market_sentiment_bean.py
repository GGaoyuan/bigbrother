from pydantic import BaseModel


class MarketSentimentBean(BaseModel):
    up_count: int
    down_count: int
    limit_up_count: int
    limit_down_count: int
    avg_change_pct: float
    total_volume: float
    max_change_pct: float
    provider: str
