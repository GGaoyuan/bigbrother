import datetime
import os
from pathlib import Path

def yesterday_str() -> str:
    cur_day = datetime.datetime.now()
    last_day = cur_day - datetime.timedelta(days=1)
    return last_day.strftime('%Y-%m-%d')
def today_str() -> str:
    cur_day = datetime.datetime.now()
    return cur_day.strftime('%Y-%m-%d')
def is_today_data() -> (bool, str):
    """
    是否使用今天的数据
    """
    cur_day = datetime.datetime.now()
    if cur_day.hour < 15:
        last_day = cur_day - datetime.timedelta(days=1)
        last_day_str = last_day.strftime('%Y-%m-%d')
        print(f'当前时间小于收盘的15点，将选用昨日{last_day_str}的数据')
        return False, last_day_str
    else:
        cur_day_str = cur_day.strftime('%Y-%m-%d')
        print(f'取用{cur_day_str}的数据')
        return True, cur_day_str

def file_path(date_str: str, file_name: str) -> str:
    """
    获取并创建data/时间的dir
    """
    current_dir = Path(__file__).parent.absolute()
    parent_dir = current_dir.parent
    data_dir = os.path.join(parent_dir, 'data')
    date_dir = os.path.join(data_dir, date_str)
    if not os.path.exists(date_dir):
        os.makedirs(date_dir)
    path = os.path.join(date_dir, file_name)
    return path