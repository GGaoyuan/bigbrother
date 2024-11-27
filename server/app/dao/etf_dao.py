from typing import Dict, Any, Iterator

from pandas import DataFrame

from app.util import md5
from app.util import time as time_util
import pandas as pd
from app.util.folder import Folder
from datetime import datetime, time, timedelta
from concurrent.futures import ThreadPoolExecutor
import akshare as ak

class ETFHistoryFolder(Folder):
    def __init__(self):
        super().__init__('datas/ETF/history')



class ETFDao:

    def __init__(self):
        pass

    def get_history_datas(self, etfs: list) -> Iterator[dict[str, DataFrame]]:
        def ak_request(etf_code: str) -> dict[str, pd.DataFrame]:
            delta = 13
            # 获取当前日期
            start_date = (datetime.now() - timedelta(delta * 3)).strftime('%Y%m%d')
            end_date = datetime.now().strftime('%Y%m%d')
            data = ak.fund_etf_hist_em(symbol=etf_code, period='daily', start_date=start_date,
                                                    end_date=end_date, adjust='qfq')
            return {etf_code: data}

        # 后期做缓存
        if time_util.is_stock_trading_time():
            # 直接请求数据
            pass
        else:
            md5_str = md5.to_string(etfs)
            folder = ETFHistoryFolder()
            today_str = datetime.now().strftime('%Y-%m-%d')


        print("多线程")
        with ThreadPoolExecutor(max_workers=len(etfs)) as executor:
            results = executor.map(ak_request, etfs)
        for result in results:
            print(result)
        print("多线程 end")
        return results


    def __get_all_list(self):
        pass