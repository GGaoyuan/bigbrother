from datetime import datetime, time

class TimeUtil:
    pass

def is_stock_trading_time() -> bool:
    """
    当前是否是交易时间，有问题，
    """
    # 获取当前时间
    now = datetime.now()
    # 定义交易时间段的开始和结束时间
    start_time = time(9, 30)
    end_time = time(15, 0)  # 下午 3 点相当于 15:00
    # 判断当前时间是否在交易时间段内
    if start_time <= now.time() < end_time:
        return True
    else:
        return False
