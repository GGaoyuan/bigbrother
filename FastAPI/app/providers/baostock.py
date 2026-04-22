import baostock as bs
from typing import Any
from .base import StockProvider


class BaoStockProvider(StockProvider):
    async def get_daily(self, code: str, start: str, end: str) -> list[dict[str, Any]]:
        lg = bs.login()
        if lg.error_code != "0":
            raise Exception(f"BaoStock 登录失败: {lg.error_msg}")
        try:
            rs = bs.query_history_k_data_plus(
                code,
                "date,open,high,low,close,volume",
                start_date=start,
                end_date=end,
                frequency="d",
                adjustflag="3",
            )
            result = []
            while rs.error_code == "0" and rs.next():
                row = rs.get_row_data()
                result.append({
                    "date": row[0],
                    "open": float(row[1]) if row[1] else 0,
                    "high": float(row[2]) if row[2] else 0,
                    "low": float(row[3]) if row[3] else 0,
                    "close": float(row[4]) if row[4] else 0,
                    "volume": float(row[5]) if row[5] else 0,
                    "code": code,
                    "provider": "baostock",
                })
            return result
        finally:
            bs.logout()

    async def get_realtime(self, code: str) -> dict[str, Any]:
        raise NotImplementedError("BaoStock 不支持实时行情")
