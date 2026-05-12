import asyncio
import akshare as ak
from app.bean import DailyBarBean, RealtimeQuoteBean, MarketSentimentBean


def _safe_float(val) -> float:
    try:
        v = float(val) if val is not None else 0.0
        return 0.0 if (v != v) else v
    except (ValueError, TypeError):
        return 0.0


class AKProvider:
    """akshare 数据提供方，优先使用同花顺数据源"""

    async def get_daily(self, code: str, start: str, end: str) -> list[DailyBarBean]:
        """获取 A 股日线数据（前复权），start/end 格式 YYYYMMDD"""
        pure_code = code.split(".")[-1] if "." in code else code
        df = await asyncio.to_thread(
            ak.stock_zh_a_hist,
            symbol=pure_code,
            period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust="qfq",
        )
        if df is None or df.empty:
            return []
        return [
            DailyBarBean(
                date=str(row.get("日期", "")),
                open=_safe_float(row.get("开盘")),
                high=_safe_float(row.get("最高")),
                low=_safe_float(row.get("最低")),
                close=_safe_float(row.get("收盘")),
                volume=_safe_float(row.get("成交量")),
                code=code,
                provider="akshare",
            )
            for _, row in df.iterrows()
        ]

    async def get_market_sentiment(self) -> MarketSentimentBean:
        """获取全市场情绪数据（同花顺数据源）"""
        df = await asyncio.to_thread(ak.stock_zh_a_spot)
        if df is None or df.empty:
            raise Exception("未获取到市场数据")

        df = df[df["最新价"].notna() & (df["最新价"] > 0)]

        up_count = int((df["涨跌幅"] > 0).sum())
        down_count = int((df["涨跌幅"] < 0).sum())
        limit_up_count = int((df["涨跌幅"] >= 9.9).sum())
        limit_down_count = int((df["涨跌幅"] <= -9.9).sum())

        near_limit_up = int(((df["涨跌幅"] >= 5) & (df["涨跌幅"] < 9.9)).sum())
        blow_rate = round(near_limit_up / limit_up_count * 100, 1) if limit_up_count > 0 else 0.0

        max_change_pct = float(df["涨跌幅"].max()) if not df.empty else 0.0
        max_streak = min(10, max(1, round(max_change_pct / 10)))

        total_volume = float(df["成交额"].sum()) if "成交额" in df.columns else 0.0

        return MarketSentimentBean(
            up_count=up_count,
            down_count=down_count,
            up_down_ratio=round(up_count / down_count, 2) if down_count > 0 else float(up_count),
            limit_up_count=limit_up_count,
            limit_down_count=limit_down_count,
            limit_ratio=round(limit_up_count / limit_down_count, 2) if limit_down_count > 0 else float(limit_up_count),
            blow_rate=blow_rate,
            max_streak=max_streak,
            total_volume=total_volume,
            volume_vs_yesterday=None,
            avg_change_pct=float(df["涨跌幅"].mean()),
            max_change_pct=max_change_pct,
            provider="akshare",
        )
