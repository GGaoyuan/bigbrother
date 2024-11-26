from app.util import md5
import pandas as pd
from . import files_util as fu
class ETFDao:

    def __init__(self):
        self.__folder = 'ETF'

    def get_history_datas(self, etfs: list) -> pd.DataFrame:
        md5_str = md5.to_string(etfs)
        fu.data_path()

        print(md5_str)


    def __get_all_list(self):
        pass