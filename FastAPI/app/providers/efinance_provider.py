import asyncio
import efinance as ef
import pandas as pd


async def get_today_capital_flow(code: str) -> pd.DataFrame:
    """
    获取单只股票/板块最新交易日的日内分钟级资金流入流出数据。

    Args:
        code: 股票代码或板块代码，如 "600519"、"000001"、"BK0457"
    """
    df = await asyncio.to_thread(ef.stock.get_today_bill, code)

    if df is None or df.empty:
        return pd.DataFrame()

    return df


