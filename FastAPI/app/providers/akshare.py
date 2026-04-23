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

    async def get_market_sentiment(self, date: str) -> dict[str, Any]:
        """获取市场统计数据（使用东方财富实时数据）"""
        df = ak.stock_zh_a_spot_em()

        if df is None or df.empty:
            raise Exception("未获取到市场数据")

        # 过滤掉无效行
        df = df[df["最新价"].notna() & (df["最新价"] > 0)]

        # 统计数据
        up_count = int((df["涨跌幅"] > 0).sum())
        down_count = int((df["涨跌幅"] < 0).sum())
        limit_up_count = int((df["涨跌幅"] >= 9.9).sum())
        limit_down_count = int((df["涨跌幅"] <= -9.9).sum())
        avg_change_pct = float(df["涨跌幅"].mean())
        total_volume = float(df["成交额"].sum()) if "成交额" in df.columns else 0
        max_change_pct = float(df["涨跌幅"].max())

        return {
            "up_count": up_count,
            "down_count": down_count,
            "limit_up_count": limit_up_count,
            "limit_down_count": limit_down_count,
            "avg_change_pct": avg_change_pct,
            "total_volume": total_volume,
            "max_change_pct": max_change_pct,
            "provider": "akshare",
        }
