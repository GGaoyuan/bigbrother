from app.util import md5
import pandas as pd
from app.util.files import STATIC_DATAS_ETF_CSV as csvf


class ETFDao:

    def __init__(self):
        pass

    def get_history_datas(self, etfs: list) -> pd.DataFrame:
        md5_str = md5.to_string(etfs)
        csv_folder = csvf()
        # folder = ETFFolder().path

        print(md5_str)


    def __get_all_list(self):
        pass