import akshare as ak
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
SPX_500_index = ak.index_us_stock_sina(symbol='.INX')
CSI_300_index = ak.stock_zh_index_daily(symbol='sh000300')

print(SPX_500_index)
# https://www.bilibili.com/video/BV13H4y1z75A/?spm_id_from=333.788&vd_source=759eb1d2871ab845edd643b39791fcfb


def rsrs(data, N, S1, S2):
    print()
    data['pct'] = data['close'] / data['close'].shift(1) - 1    #shift(1)是取下一个值
    def calculate_beta(df, window = N):
        if df.shape[0] < window:
            return np.nan
        x = df['low'].values
        y = df['high'].values
        beta = LinearRegression().fit(x.reshape(-1, 1), y.reshape(-1, 1)).coef_[0]
        return beta
    data['beta'] = [calculate_beta(df, window=N) for df in data.rolling(window=N)]
    delta = data.dropna().copy().reset_index(drop=True)

    delta['flag'] = 0
    delta['position'] = 0
    position = 0

    for i in range(1, delta.shape[0] -1):
        beta = delta.loc[i, 'beta']
        if (position == 0) and (beta > S1):
            delta.loc[i, 'flag'] = 1
            delta.loc[i+1, 'position'] = 1
            position = 1
        elif (position == 1) and (beta < S2):
            delta.loc[i, 'flag'] = -1
            delta.loc[i + 1, 'position'] = 0
            position = 0
        else:
            delta.loc[i + 1, 'position'] = delta.loc[i, 'position']



df = pd.DataFrame({
    'close': [1, 2, 3, 4, 5, 6, 7]
})
print(df)
df = rsrs(data=df, N=1, S1=1, S2=2)
print(df)