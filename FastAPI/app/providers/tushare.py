import tushare as ts
from typing import Any
from .base import StockProvider
from app.core.config import settings


class TuShareProvider(StockProvider):
    def __init__(self):
        self._pro = ts.pro_api(settings.tushare_token)

    async def get_daily(self, code: str, start: str, end: str) -> list[dict[str, Any]]:
        # TuShare 股票代码格式：600000.SH 或 000001.SZ
        ts_code = self._to_ts_code(code)
        start_fmt = start.replace("-", "")
        end_fmt = end.replace("-", "")
        df = self._pro.daily(ts_code=ts_code, start_date=start_fmt, end_date=end_fmt)
        result = []
        for _, row in df.iterrows():
            result.append({
                "date": f"{row['trade_date'][:4]}-{row['trade_date'][4:6]}-{row['trade_date'][6:]}",
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["vol"]),
                "code": code,
                "provider": "tushare",
            })
        return result

    async def get_realtime(self, code: str) -> dict[str, Any]:
        raise NotImplementedError("TuShare 免费版不支持实时行情")

    @staticmethod
    def _to_ts_code(code: str) -> str:
        # sh.600000 -> 600000.SH, sz.000001 -> 000001.SZ
        if "." in code:
            prefix, num = code.split(".")
            return f"{num}.{prefix.upper()}"
        return code
