from typing import List, Optional
from pydantic import BaseModel
import asyncio

import akshare as ak
import pandas as pd


class ThsIndividualNetInflow(BaseModel):
    """
    同花顺-个股资金流向数据（即时/全市场快照）
    数据源: akshare ak.stock_fund_flow_individual(symbol="即时")
    """

    # 股票代码
    stock_code: Optional[str] = None

    # 股票名称
    stock_name: Optional[str] = None

    # 最新价
    price: Optional[float] = None

    # 涨跌幅（%）
    change_pct: Optional[float] = None

    # 换手率（%）
    turnover_rate: Optional[float] = None

    # 流入资金（元）
    fund_inflow: Optional[float] = None

    # 流出资金（元）
    fund_outflow: Optional[float] = None

    # 资金净流入（元）= 流入 - 流出
    fund_net_inflow: Optional[float] = None

    # 成交额（元）
    turnover: Optional[float] = None


# 单位换算系数：同花顺金额带单位的字符串
_UNIT_MULTIPLIER = {
    "万": 1e4,
    "亿": 1e8,
    "千": 1e3,
}


def _parse_percent(val) -> Optional[float]:
    """解析带百分号的字符串，如 '20.21%' -> 20.21"""
    if val is None or pd.isna(val):
        return None
    try:
        return float(str(val).strip().rstrip("%"))
    except (ValueError, TypeError):
        return None


def _parse_amount(val) -> Optional[float]:
    """解析带单位的金额字符串，如 '6.22亿' -> 622_000_000.0，'-1.41亿' -> -141_000_000.0"""
    if val is None or pd.isna(val):
        return None
    s = str(val).strip()
    if not s:
        return None
    # 检查最后一个字符是否是单位
    unit = s[-1]
    if unit in _UNIT_MULTIPLIER:
        try:
            return float(s[:-1]) * _UNIT_MULTIPLIER[unit]
        except (ValueError, TypeError):
            return None
    # 没有单位时，按纯数字处理
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


async def get_ths_individual_net_inflow() -> List[ThsIndividualNetInflow]:
    """
    获取同花顺全市场个股资金流向（即时快照）。

    映射:
        股票代码 -> stock_code, 股票简称 -> stock_name,
        最新价 -> price, 涨跌幅 -> change_pct, 换手率 -> turnover_rate,
        流入资金 -> fund_inflow, 流出资金 -> fund_outflow,
        净额 -> fund_net_inflow, 成交额 -> turnover

    注意：原始数据中金额带单位（亿/万），涨跌幅/换手率带百分号，本方法已解析为元/百分点。
    """
    df = await asyncio.to_thread(ak.stock_fund_flow_individual, symbol="即时")
    if df is None or df.empty:
        return []
    return [
        ThsIndividualNetInflow(
            # 股票代码原始为整数，补 0 到 6 位
            stock_code=str(row["股票代码"]).zfill(6) if pd.notna(row.get("股票代码")) else None,
            stock_name=str(row.get("股票简称")) if pd.notna(row.get("股票简称")) else None,
            price=float(row["最新价"]) if pd.notna(row.get("最新价")) else None,
            change_pct=_parse_percent(row.get("涨跌幅")),
            turnover_rate=_parse_percent(row.get("换手率")),
            fund_inflow=_parse_amount(row.get("流入资金")),
            fund_outflow=_parse_amount(row.get("流出资金")),
            fund_net_inflow=_parse_amount(row.get("净额")),
            turnover=_parse_amount(row.get("成交额")),
        )
        for _, row in df.iterrows()
    ]
