from ..dao.ranking import *
from ..service import *
def get_hot_by_rank(start_date: str, end_date: str):
    """
    获取龙虎榜和相关的数据
    """
    # 获取龙虎榜的数据列表
    # 判断龙虎榜的数据归属
    # 我是看资金流入量打板的，在10点20分左右监测到有大资
    leader_list = get_leader_list(start_date, end_date)
    print(leader_list)