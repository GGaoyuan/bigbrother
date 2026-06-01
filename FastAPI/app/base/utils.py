from typing import List, Optional
import pandas as pd
def to_float(val) -> Optional[float]:
    """安全转换为浮点数，遇异常或 NaN 返回 None"""
    try:
        if val is None or pd.isna(val):
            return None
        return float(val)
    except (ValueError, TypeError):
        return None