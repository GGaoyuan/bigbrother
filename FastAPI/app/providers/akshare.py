import akshare as ak
from typing import Any
from .base import StockProvider


class AKShareProvider(StockProvider):
    async def get_daily(self, code: str, start: str, end: str) -> list[dict[str, Any]]:
        # AKShare 股票代码格式：去掉交易所前缀，如 sh.600000 -> 600000
        pure_code = code.split(".")[-1] if "." in code else code
        start_fmt = start.replace("-", "")
        end_fmt = end.replace("-", "")
        df = ak.stock_zh_a_hist(
            symbol=pure_code,
            period="daily",
            start_date=start_fmt,
            end_date=end_fmt,
            adjust="qfq",
        )
        result = []
        for _, row in df.iterrows():
            result.append({
                "date": str(row["日期"]),
                "open": float(row["开盘"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "close": float(row["收盘"]),
                "volume": float(row["成交量"]),
                "code": code,
                "provider": "akshare",
            })
        return result

    async def get_realtime(self, code: str) -> dict[str, Any]:
        pure_code = code.split(".")[-1] if "." in code else code
        df = ak.stock_zh_a_spot_em()
        row = df[df["代码"] == pure_code]
        if row.empty:
            raise Exception(f"未找到股票: {code}")
        r = row.iloc[0]
        return {
            "code": code,
            "name": r["名称"],
            "price": float(r["最新价"]),
            "change": float(r["涨跌额"]),
            "change_pct": float(r["涨跌幅"]),
            "volume": float(r["成交量"]),
            "provider": "akshare",
        }
