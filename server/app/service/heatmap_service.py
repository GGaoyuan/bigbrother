from app.dao import industry_board
from app.dao.etf_dao import ETFDao
from app.dao.industry_board import IndustryDao
from concurrent.futures import ThreadPoolExecutor
from pandas import DataFrame

class HeatmapService:
    def __init__(self):
        pass

    @staticmethod
    def get_industry_history_data() -> list:
        """
        获取行业板块的历史数据
        :return:
        """
        industry_list: list[dict] = IndustryDao.get_industries_list()
        industry_list = industry_list[:5]
        industry_name = '板块名称'
        with ThreadPoolExecutor(max_workers=len(industry_list)) as executor:
            results = executor.map(lambda arg: IndustryDao.get_industries_history_daily(arg, 13), [d[industry_name] for d in industry_list])
        for index, row in enumerate(results):
            name = row['name']
            history: list = row['history_list']
            history.sort(key=lambda x: x['日期'], reverse=True)
            match = next((d for d in industry_list if d.get(industry_name) == name), None)
            if match is not None:
                match['history_list'] = history
        return industry_list

    @staticmethod
    def get_concept_history_data() -> list:
        """
        获取概念板块的历史数据
        :return:
        """
        pass

    @staticmethod
    def get_aaa():
        # 大盘因子：板块中上涨的票和下跌的票比例
        # 将n天的行业板块的涨跌幅相加，概念涨跌古相加，获取前m个，看交集，获取强势板块
        pass