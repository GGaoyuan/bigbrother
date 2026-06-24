from datetime import datetime, timedelta
from typing import List


def recent_trade_dates(n: int = 5) -> List[str]:
    """返回最近 n 个可能的交易日日期（YYYYMMDD），排除周末，倒序（最近的在前）。

    n: 返回的候选日期数量
    """
    result: List[str] = []
    date = datetime.now().date()
    while len(result) < n:
        # 排除周末（0=周一, 6=周日）
        if date.weekday() < 5:
            result.append(date.strftime("%Y%m%d"))
        date -= timedelta(days=1)
    return result
