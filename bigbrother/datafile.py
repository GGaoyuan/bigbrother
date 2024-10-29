from pathlib import Path
import os
import datetime, time

def datas_dir() -> str:
    """
    创建datas文件夹
    """
    folder_path = os.path.join(Path(__file__).parent.absolute().parent, 'datas')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def file_path(file_name: str) -> str:
    data_folder = datas_dir()
    file_address = os.path.join(data_folder, file_name)
    return file_address

def get_file_path(file_name: str, date: datetime = datetime.date.today()) -> str:
    # 老方法，别用了
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
