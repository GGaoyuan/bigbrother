from enum import Enum


class CachePolicy(Enum):
    """
    缓存策略，按自然时间边界判断鲜度（非固定秒数 TTL）。

    DAILY:   当天有效，次日 0 点后可刷新（如 9:00 拉取，次日 0:00 起可更新）
    WEEKLY:  当周有效，下周一 0 点后可刷新
    MONTHLY: 当月有效，下月 1 日 0 点后可刷新
    NONE:    实时获取，不缓存
    """

    NONE = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
