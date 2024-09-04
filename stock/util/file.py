import enum
from pathlib import Path
import os
import datetime, time

# 市场上的所有票
market_stock_csv = 'market_stock.csv'
# 市场上可交易的票
market_tradable_stock_csv = 'market_tradable_stock.csv'

def get_file_path(file_name: str, date: datetime = datetime.date.today()) -> str:
    # 提取文件名（不含扩展名）作为文件夹名
    current_dir = Path(__file__).parent.absolute()
    parent_dir = current_dir.parent
    target_dir = os.path.join(parent_dir, 'datas')
    # 拼接当前工作目录和文件夹名，创建完整的文件夹路径
    date_str = date.strftime('%Y-%m-%d')
    date_dir = os.path.join(target_dir, date_str)
    # 如果文件夹不存在，则创建它
    if not os.path.exists(date_dir):
        os.makedirs(date_dir)
        # 拼接文件夹路径和文件名，形成完整的文件地址
    file_address = os.path.join(date_dir, file_name)
    return file_address