from enum import Enum
import pandas as pd

class CandleMode(Enum):
    HAMMER_HANGING = 1  #锤子线/上吊线

def mode(open: float, close: float, high: float, low: float) -> CandleMode:
    return CandleMode.HAMMER_HANGING


def hammer_hanging_man(df):

    results = []

    for index, row in df.iterrows():
        open_price = row['open']
        close_price = row['close']
        high_price = row['high']
        low_price = row['low']

        # 计算实体和影线长度
        real_body = abs(close_price - open_price)
        lower_shadow = open_price - low_price if close_price > open_price else close_price - low_price
        upper_shadow = high_price - close_price if close_price > open_price else high_price - open_price

        # 定义长下影线和短上影线的标准
        is_long_lower_shadow = lower_shadow >= 2 * real_body
        is_short_upper_shadow = upper_shadow <= 0.3 * real_body

        # 判断是否为锤子线或上吊线
        if is_long_lower_shadow and is_short_upper_shadow:
            if close_price > open_price:
                pattern = 'Hammer' if index > 0 and df.loc[index - 1, 'close'] < close_price else 'Hanging Man'
            else:
                pattern = 'Hammer' if index > 0 and df.loc[index - 1, 'close'] < close_price else 'Hanging Man'

            results.append({'index': index, 'pattern': pattern})

    return pd.DataFrame(results)

# 示例调用
# result_df = identify_hammer_hanging_man(df)
# print(result_df)