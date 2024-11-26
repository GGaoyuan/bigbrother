from app.util import md5
from app.util import time as time_util
import pandas as pd
from app.util.folder import Folder
from datetime import datetime, time

class ETFHistoryFolder(Folder):
    def __init__(self):
        super().__init__('datas/ETF/history')

        

class ETFDao:

    def __init__(self):
        pass

    def get_history_datas(self, etfs: list) -> pd.DataFrame:
        if time_util.is_stock_trading_time():
            # 直接请求数据
            pass
        else:
            md5_str = md5.to_string(etfs)
            folder = ETFHistoryFolder()
            today_str = datetime.now().strftime('%Y-%m-%d')
        # folder = ETFFolder().path

        print(md5_str)


    def __get_all_list(self):
        pass