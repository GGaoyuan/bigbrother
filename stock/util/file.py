import enum
from pathlib import Path
import os
import datetime, time

# 市场上的所有票
stock_list_all = 'stock_list_all'


def get_scv_path(file_name: str, date: datetime = datetime.date.today()) -> str:
    # 提取文件名（不含扩展名）作为文件夹名
    current_dir = Path(__file__).parent.absolute()
    parent_dir = current_dir.parent
    datas_dir = os.path.join(parent_dir, 'datas')
    # 拼接文件名
    file_dir = os.path.join(datas_dir, file_name)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 拼接日期
    date_str = date.strftime('%Y-%m-%d')
    csv_file = date_str + '.csv'
    file_path = os.path.join(file_dir, date_str)
    return file_path

# path = get_scv_path(stock_list_all, date=datetime.date(2023, 11, 3))
# print(path)