import akshare as ak
from pandas import DataFrame

class DateDao:
    def __init__(self):
        pass

    @staticmethod
    def get_trade_date() -> DataFrame:
        """
        获取交易日数据
        :return:
        """
        tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
        return tool_trade_date_hist_sina_df
