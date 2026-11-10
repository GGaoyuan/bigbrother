"""通过 AKShare 现成接口读取沪深两融汇总，不自行抓取、不缓存。"""

from datetime import date, timedelta

import akshare as ak
from pandas import DataFrame


def get_sse_margin(end_date: date) -> DataFrame:
    """通过 AKShare 获取沪市原始日汇总，额外保留一日供计算。

    Args:
        end_date: 查询截止日期。
    """
    try:
        return ak.stock_margin_sse(
            start_date=(end_date - timedelta(days=60)).strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )
    except ValueError as exc:
        # AKShare 1.20.37 对空结果赋 13 个列名时会抛出此异常。
        # 只识别已核实的空表异常，其余结构变化继续向上报告。
        if str(exc) != "Length mismatch: Expected axis has 0 elements, new values have 13 elements":
            raise
        return DataFrame()


def get_szse_margin(trade_date: date) -> DataFrame:
    """通过 AKShare 获取深市指定交易日原始汇总。

    Args:
        trade_date: 交易日期；该库返回金额单位为亿元，数量为亿股/亿份。
    """
    try:
        return ak.stock_margin_szse(date=trade_date.strftime("%Y%m%d"))
    except ValueError as exc:
        # 已实测：非交易日空结果会触发库内列名赋值错误，而非返回空表。
        if str(exc) != "Length mismatch: Expected axis has 0 elements, new values have 6 elements":
            raise
        return DataFrame()
