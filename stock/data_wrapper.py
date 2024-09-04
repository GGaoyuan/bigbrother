import akshare as ak
import adata
import pandas as pd

def get_market(stock_code: str, start_date: str = '1990-01-01', end_date=None, k_type=1,
                   adjust_type: int = 1) -> pd.DataFrame:
    df = adata.stock.market.get_market(stock_code = stock_code, start_date = start_date, end_date = end_date, k_type = k_type, adjust_type = adjust_type)
    df['openinterest'] = 0
    df['date'] = df['trade_date']
    df.index = pd.to_datetime(df['date'])
    df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']].copy()
    return df

