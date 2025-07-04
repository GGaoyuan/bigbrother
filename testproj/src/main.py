# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def analyze_stock_data():
    # 1. 获取股票代码列表（上证A股）
    sh_stock_list = ak.stock_info_sh_name_code(symbol="主板A股")
    # 随机选择3只股票
    selected_stocks = sh_stock_list.sample(3)[['证券代码', '证券简称']]
    print("随机选取的股票:")
    print(selected_stocks)
    print("\n" + "=" * 80 + "\n")

    # 2. 获取最近一个月的历史数据
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

    results = []

    for idx, row in selected_stocks.iterrows():
        stock_code = row['证券代码']
        stock_name = row['证券简称']

        try:
            # 获取个股历史数据
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                    start_date=start_date, end_date=end_date,
                                    adjust="qfq")

            # 3. 使用Pandas进行数据处理
            df['日期'] = pd.to_datetime(df['日期'])
            df.set_index('日期', inplace=True)

            # 4. 使用NumPy计算技术指标
            # 计算5日和20日移动平均线
            df['MA5'] = np.round(np.convolve(df['收盘'], np.ones(5) / 5, mode='valid'), 2)
            df['MA20'] = np.round(np.convolve(df['收盘'], np.ones(20) / 20, mode='valid'), 2)

            # 计算相对强弱指标 (RSI)
            delta = df['收盘'].diff()
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            avg_gain = np.convolve(gain, np.ones(14) / 14, mode='valid')
            avg_loss = np.convolve(loss, np.ones(14) / 14, mode='valid')
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            # 对齐RSI数据
            rsi = np.concatenate([np.full(df.shape[0] - len(rsi), np.nan), rsi])
            df['RSI'] = np.round(rsi, 2)

            # 获取最新数据
            latest = df.iloc[-1]
            prev_day = df.iloc[-2]

            # 分析结果
            trend = "上涨趋势 ↗" if latest['MA5'] > latest['MA20'] else "下跌趋势 ↘"
            volatility = np.std(df['收盘'][-5:])  # 最近5日波动率

            results.append({
                "股票代码": stock_code,
                "股票名称": stock_name,
                "收盘价": latest['收盘'],
                "涨跌幅(%)": round((latest['收盘'] - prev_day['收盘']) / prev_day['收盘'] * 100, 2),
                "5日均价": latest['MA5'],
                "20日均价": latest['MA20'],
                "RSI": latest['RSI'],
                "趋势": trend,
                "波动率": round(volatility, 4)
            })

        except Exception as e:
            print(f"处理股票 {stock_name}({stock_code}) 时出错: {str(e)}")

    # 5. 打印结果
    if results:
        print("\n股票分析结果:")
        print("=" * 110)
        print(
            f"{'代码':<8}{'名称':<10}{'收盘价':<8}{'涨跌幅(%)':<10}{'5日均价':<8}{'20日均价':<8}{'RSI':<6}{'趋势':<12}{'波动率':<8}")
        print("-" * 110)

        for r in results:
            color_code = '\033[92m' if r['涨跌幅(%)'] >= 0 else '\033[91m'  # 绿色表示上涨，红色表示下跌
            reset_code = '\033[0m'

            print(f"{r['股票代码']:<8}{r['股票名称']:<10}"
                  f"{r['收盘价']:<8.2f}"
                  f"{color_code}{r['涨跌幅(%)']:<10.2f}{reset_code}"
                  f"{r['5日均价']:<8.2f}"
                  f"{r['20日均价']:<8.2f}"
                  f"{r['RSI']:<6.1f}"
                  f"{r['趋势']:<12}"
                  f"{r['波动率']:<8.4f}")


def print_hi(name):
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    print("开始执行股票数据分析...")
    print("获取数据并计算技术指标，请稍候...\n")
    analyze_stock_data()
    print("\n分析完成！")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
