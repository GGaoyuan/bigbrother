from app.dao.etf_dao import ETFDao
from app.dao.industry_dao import IndustryDao


class HeatmapService:
    def __init__(self):
        self.__etf_dao = ETFDao()
        self.__industry_dao = IndustryDao()

    def get_etfs_history_data(self) -> str:
        """
        获取etf的历史数据
        """
        etf_list = [
            '159755', #电池ETF
            '159996', #家电ETF
        ]
        datas = self.__etf_dao.get_history_datas(etf_list)

        # print(datas)

        return ""

    def get_industry_history_data(self) -> str:
        """
        获取板块的历史数据
        """
        datas = self.__industry_dao.get_industries_hist_daily()

        # print(datas)

        return ""