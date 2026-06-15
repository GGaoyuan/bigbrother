from datetime import datetime

from .policy import CachePolicy


def is_cache_fresh(
    cached_at: datetime,
    policy: CachePolicy,
    now: datetime | None = None,
) -> bool:
    """按自然日/周/月边界判断缓存是否仍有效。"""
    if policy == CachePolicy.NONE:
        return False

    now = now or datetime.now()

    if policy == CachePolicy.DAILY:
        return cached_at.date() == now.date()

    if policy == CachePolicy.WEEKLY:
        return cached_at.isocalendar()[:2] == now.isocalendar()[:2]

    if policy == CachePolicy.MONTHLY:
        return cached_at.year == now.year and cached_at.month == now.month

    return False
