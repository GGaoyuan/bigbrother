from app.dao.etf_dao import ETFDao
class HeatmapService:
    def __init__(self):
        self.__etf_dao = ETFDao()

    def get_etfs_history_data(self) -> str:
        """
        获取etf的历史数据
        """
        etf_list = [
            '159755', #电池ETF
            '159996', #家电ETF
        ]
        df = self.__etf_dao.get_history_datas(etf_list)
        print(df)

        return ""
