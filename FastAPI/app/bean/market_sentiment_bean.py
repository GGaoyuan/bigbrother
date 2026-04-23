from pydantic import BaseModel
from typing import Optional


class MarketSentimentBean(BaseModel):
    """市场情绪数据 Bean"""

    # 涨跌统计
    up_count: int  # 上涨股票数量
    down_count: int  # 下跌股票数量
    up_down_ratio: float  # 涨跌比例（上涨数/下跌数）

    # 涨跌停统计
    limit_up_count: int  # 涨停股票数量
    limit_down_count: int  # 跌停股票数量
    limit_ratio: float  # 涨跌停比例（涨停数/跌停数）

    # 市场特征
    blow_rate: float  # 炸板率（%）：涨幅在 5~9.9% 之间的股票数占涨停数的比例
    max_streak: int  # 最高连板数（板）：根据最高涨幅近似计算

    # 成交量
    total_volume: float  # 总成交额（元）
    volume_vs_yesterday: Optional[float] = None  # 成交量相较昨日变化（%），可能为空

    # 涨跌幅
    avg_change_pct: float  # 平均涨跌幅（%）
    max_change_pct: float  # 最大涨幅（%）

    # 数据源
    provider: str  # 数据提供方（如 akshare）
