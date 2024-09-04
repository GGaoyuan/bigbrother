import akshare as ak
import pandas as pd

def get_market(stock_code: str = '000001', start_date: str = '1990-01-01', end_date=None, k_type=1,
                   adjust_type: int = 1) -> pd.DataFrame:
    df = ak.stock.market.get_market(stock_code=stock_code, start_date=start_date, end_date=end_date,
                                     k_type=k_type, adjust_type=adjust_type)
    print(df)
    return df


df = get_market(stock_code='000001')
print(df)

print('aaaaaaaa')