from app.dao.concept_board import ConceptDao
from app.dao.industry_board import IndustryDao
from concurrent.futures import ThreadPoolExecutor

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
        # industry_list = industry_list[:5]
        industry_name = '板块名称'
        with ThreadPoolExecutor(max_workers=len(industry_list)) as executor:
            results = executor.map(lambda arg: IndustryDao.get_industries_history_daily(arg, 60), [d[industry_name] for d in industry_list])
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
        concept_list: list[dict] = ConceptDao.get_concepts_list()
        concept_list = concept_list[:6]
        concept_name = '板块名称'
        with ThreadPoolExecutor(max_workers=len(concept_list)) as executor:
            results = executor.map(lambda arg: ConceptDao.get_concepts_history_daily(arg, 13), [d[concept_name] for d in concept_list])
        for index, row in enumerate(results):
            name = row['name']
            history: list = row['history_list']
            history.sort(key=lambda x: x['日期'], reverse=True)
            match = next((d for d in concept_list if d.get(concept_name) == name), None)
            if match is not None:
                match['history_list'] = history
        return concept_list



    @staticmethod
    def get_aaa():
        # 大盘因子：板块中上涨的票和下跌的票比例
        # 将n天的行业板块的涨跌幅相加，概念涨跌古相加，获取前m个，看交集，获取强势板块
        # 汇总n天内，涨幅最高的行业板块和概念板块

        # 各个主板。创业板的数据


        # 看了蜡烛图的趋势线和极性反转，我需要寻找一些散户比较多（小单交易比较多的票，验证一下是否符合他的原则）
        pass