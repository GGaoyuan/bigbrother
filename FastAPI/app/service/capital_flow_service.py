from datetime import date as date_cls
from typing import List, Optional
import asyncio

from app.providers.efinance_provider import get_today_capital_flow
from app.base.datasource_from import DatasourceFrom
from app.model.capital_flow_model import CapitalFlowModel
from app.model.today_capital_flow_model import TodayCapitalFlowModel


async def get_today_capital_flow_by_codes(
    codes: List[str],
) -> List[TodayCapitalFlowModel]:
    """
    批量获取多只股票/板块今日的日内分钟级资金流入流出数据，按代码分组返回。

    Args:
        codes: 股票代码或板块代码数组，例如 ["600519", "000001", "BK0457"]
    """
    if not codes:
        return []

    dfs = await asyncio.gather(
        *(get_today_capital_flow(code) for code in codes)
    )

    result: List[TodayCapitalFlowModel] = []
    for code, df in zip(codes, dfs):
        if df is None or df.empty:
            continue

        flows = [
            CapitalFlowModel(
                stock_code=row["股票代码"],
                time=row["时间"],
                main_net_inflow=row["主力净流入"],
                small_order_inflow=row["小单净流入"],
                medium_order_inflow=row["中单净流入"],
                large_order_inflow=row["大单净流入"],
                extra_large_order_inflow=row["超大单净流入"],
                datasource=DatasourceFrom.EAST_MONEY,
            )
            for _, row in df.iterrows()
        ]

        result.append(TodayCapitalFlowModel(stock_code=code, flows=flows))

    return result
