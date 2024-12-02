from app.dao import industry_dao
from app.dao.etf_dao import ETFDao
from app.dao.industry_dao import IndustryDao
from concurrent.futures import ThreadPoolExecutor
from pandas import DataFrame

class HeatmapService:
    def __init__(self):
        pass



    def get_industry_history_data(self) -> list:
        """
        获取板块的历史数据
        """
        industry_list = IndustryDao.get_board_industries_list()
        # industry_name_list = industry_list[['板块名称']]
        industry_list = industry_list[:1]
        result_list:list = []
        with ThreadPoolExecutor(max_workers=len(industry_list)) as executor:
            for index, row in industry_list.iterrows():
                industry_name = row['板块名称']
                result = executor.submit(IndustryDao.get_board_industries_hist_daily, industry_name, 13)
                result_list.append({'industry': row, 'history': result.result()})
                # history = result.result().to
                # results.append(result)
                # row['history'] = result.result()

        # for index, row in industry_list.iterrows():
        #     print(row)
        #     history = row['history']
        #     print(history)
        return result_list