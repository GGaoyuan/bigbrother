from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal


TtlKind = Literal["rolling", "daily", "weekly", "monthly"]


@dataclass(frozen=True)
class CacheTTL:
    """缓存有效期。

    HOURLY 是滚动 TTL（写入后 1 小时失效），DAILY/WEEKLY/MONTHLY 是自然时间边界
    （当天/当周/当月内有效）。也可以用 rolling(seconds=N) 自定义滚动 TTL。
    """

    kind: TtlKind
    rolling_seconds: int = 0

    @staticmethod
    def rolling(seconds: int) -> "CacheTTL":
        return CacheTTL(kind="rolling", rolling_seconds=seconds)

    def expires_at(self, cached_at: datetime) -> datetime:
        """根据写入时间算出失效时间（>= 该时间表示已过期）。"""
        if self.kind == "rolling":
            return cached_at + timedelta(seconds=self.rolling_seconds)
        if self.kind == "daily":
            next_day = (cached_at + timedelta(days=1)).date()
            return datetime(next_day.year, next_day.month, next_day.day)
        if self.kind == "weekly":
            # 失效时间为下周一 0 点
            days_to_monday = 7 - cached_at.weekday()
            target = (cached_at + timedelta(days=days_to_monday)).date()
            return datetime(target.year, target.month, target.day)
        if self.kind == "monthly":
            year = cached_at.year + (1 if cached_at.month == 12 else 0)
            month = 1 if cached_at.month == 12 else cached_at.month + 1
            return datetime(year, month, 1)
        raise ValueError(f"未知的 TTL kind: {self.kind}")

    def is_fresh(self, cached_at: datetime, now: datetime | None = None) -> bool:
        return (now or datetime.now()) < self.expires_at(cached_at)


CacheTTL.HOURLY = CacheTTL(kind="rolling", rolling_seconds=3600)
CacheTTL.DAILY = CacheTTL(kind="daily")
CacheTTL.WEEKLY = CacheTTL(kind="weekly")
CacheTTL.MONTHLY = CacheTTL(kind="monthly")
