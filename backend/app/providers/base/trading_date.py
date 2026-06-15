from datetime import datetime, timedelta


def recent_trade_dates(max_days: int = 10) -> list[str]:
    """生成最近若干自然日，用于非交易日接口回退。"""
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(max_days)]
