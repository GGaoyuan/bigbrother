from pydantic import BaseModel


class TodayBillBean(BaseModel):
    """
    日内分钟级单子流入流出数据 Bean
    对应 efinance ef.stock.get_today_bill 接口返回的数据结构
    """

    time: str                     # 时间，格式 HH:MM，如 09:31
    main_net_inflow: float        # 主力净流入（元）
    small_net_inflow: float       # 小单净流入（元）
    medium_net_inflow: float      # 中单净流入（元）
    large_net_inflow: float       # 大单净流入（元）
    super_large_net_inflow: float # 超大单净流入（元）
