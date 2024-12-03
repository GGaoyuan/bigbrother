from datetime import datetime, timedelta
import akshare as ak



class ConceptDao:
    def __init__(self):
        pass

    @staticmethod
    def get_concepts_list() -> list[dict]:
        """
        返回概念板块列表
        :return: list[dict]
        """
        df = ak.stock_board_concept_name_em()
        result = df.to_dict(orient='records')
        return result

    @staticmethod
    def get_concepts_history_daily(concept_name: str, time_delta = 0) -> dict:
        """
        获取概念板块日级历史数据
        :param concept_name: 板块名称
        :param time_delta: 多少天前
        :return: DataFrame
        """
        keys = ('name', 'history_list')
        rtn = {
            keys[0]: concept_name,
            keys[1]: []
        }
        try:
            # 获取当前日期
            start_date = (datetime.now() - timedelta(time_delta)).strftime('%Y%m%d')
            end_date = datetime.now().strftime('%Y%m%d')
            if time_delta == 0:
                end_date = start_date
            cons_df = ak.stock_board_concept_hist_em(symbol=concept_name, period='daily', start_date=start_date,
                                                      end_date=end_date, adjust='qfq')
            rtn[keys[1]] = cons_df.to_dict(orient='records')
            return rtn
        except Exception as e:
            print(f"{concept_name} 数据获取失败: {e}")
            return rtn
