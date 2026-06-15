from typing import Dict, List, Optional

import pandas as pd


def calc_ma(series: pd.Series, window: int) -> Optional[float]:
    if len(series) < window:
        return None
    return round(float(series.tail(window).mean()), 4)


def find_support_resistance(
    df: pd.DataFrame,
    price_col: str = "close",
    lookbacks: Optional[List[int]] = None,
) -> Dict[str, Optional[float]]:
    """基于历史高低点识别支撑位/压力位。"""
    lookbacks = lookbacks or [60, 120]
    result: Dict[str, Optional[float]] = {}
    if df.empty or price_col not in df.columns:
        return result

    prices = df[price_col].astype(float)
    for days in lookbacks:
        segment = prices.tail(days)
        if segment.empty:
            result[f"support_{days}"] = None
            result[f"resistance_{days}"] = None
            continue
        result[f"support_{days}"] = round(float(segment.min()), 4)
        result[f"resistance_{days}"] = round(float(segment.max()), 4)
    return result


def enrich_index_indicators(rows: List[dict]) -> List[dict]:
    """为指数日K数据补充均线与趋势标签。"""
    if not rows:
        return rows

    df = pd.DataFrame(rows)
    if "close" not in df.columns:
        return rows

    closes = df["close"].astype(float)
    ma_windows = [5, 10, 20, 60, 120, 250]
    for window in ma_windows:
        df[f"ma{window}"] = closes.rolling(window, min_periods=1).mean().round(4)

    latest = df.iloc[-1]
    ma_values = [latest.get(f"ma{w}") for w in [5, 10, 20, 60]]
    valid = [v for v in ma_values if v is not None and not pd.isna(v)]
    if len(valid) >= 2:
        if all(valid[i] >= valid[i + 1] for i in range(len(valid) - 1)):
            trend = "bull"
        elif all(valid[i] <= valid[i + 1] for i in range(len(valid) - 1)):
            trend = "bear"
        else:
            trend = "range"
    else:
        trend = "unknown"

    sr = find_support_resistance(df.rename(columns={"close": "close"}))
    enriched = df.to_dict(orient="records")
    if enriched:
        enriched[-1]["trend"] = trend
        enriched[-1].update(sr)
    return enriched
