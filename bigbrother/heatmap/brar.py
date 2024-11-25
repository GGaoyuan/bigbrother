"""
情绪指标BRAR
"""
import pandas as pd


class BRAR:
    def __init__(self):
        pass



def BR(df, n):
    high_ref_close = df['HIGH'] - df['CLOSE'].shift(1)
    high_ref_close = high_ref_close.where(high_ref_close > 0, 0)  # MAX(0, HIGH - REF(CLOSE, 1))
    sum_high_ref_close = high_ref_close.rolling(window=n, min_periods=1).sum()

    ref_close_low = df['CLOSE'].shift(1) - df['LOW']
    ref_close_low = ref_close_low.where(ref_close_low > 0, 0)  # MAX(0, REF(CLOSE, 1) - LOW)
    sum_ref_close_low = ref_close_low.rolling(window=n, min_periods=1).sum()

    br = sum_high_ref_close / sum_ref_close_low * 100
    return br


def AR(df, n):
    sum_high_open = (df['HIGH'] - df['OPEN']).rolling(window=n, min_periods=1).sum()
    sum_open_low = (df['OPEN'] - df['LOW']).rolling(window=n, min_periods=1).sum()

    ar = sum_high_open / sum_open_low * 100
    return ar



data = {
    # 'CLOSE': 填每日收盘的数据,
    # 'HIGH': 填每日最高的数据,
    # 'LOW': 填每日最低的数据
    # 'OPEN': 填每日开盘的数据
}


df = pd.DataFrame(data)

# 计算BR和AR指标
n = 26  # N的值
df['BR'] = BR(df, n)
df['AR'] = AR(df, n)

print(df)