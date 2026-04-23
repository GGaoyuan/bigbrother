import asyncio
import akshare as ak
from .base import StockProvider
from app.bean import DailyBarBean, RealtimeQuoteBean, MarketSentimentBean


class AKShareProvider(StockProvider):
    """AKShare 数据提供方，优先使用东方财富数据源"""

    def __init__(self):
        # 设置 akshare 的请求超时时间（如果支持）
        pass

    async def _fetch_with_retry(self, func, *args, max_retries=3, **kwargs):
        """带重试机制的数据获取"""
        for attempt in range(max_retries):
            try:
                return await asyncio.to_thread(func, *args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"请求失败（已重试 {max_retries} 次）: {str(e)}")
                await asyncio.sleep(1)  # 重试前等待 1 秒

    async def get_daily(self, code: str, start: str, end: str) -> list[DailyBarBean]:
        """获取 A 股日线数据（前复权）"""
        # AKShare 股票代码格式：去掉交易所前缀，如 sh.600000 -> 600000
        pure_code = code.split(".")[-1] if "." in code else code
        df = await self._fetch_with_retry(
            ak.stock_zh_a_hist,
            symbol=pure_code,
            period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust="qfq",
        )
        return [
            DailyBarBean(
                date=str(row["日期"]),
                open=float(row["开盘"]),
                high=float(row["最高"]),
                low=float(row["最低"]),
                close=float(row["收盘"]),
                volume=float(row["成交量"]),
                code=code,
                provider="akshare",
            )
            for _, row in df.iterrows()
        ]

    async def get_realtime(self, code: str) -> RealtimeQuoteBean:
        """获取 A 股实时行情（东方财富）"""
        pure_code = code.split(".")[-1] if "." in code else code
        df = await self._fetch_with_retry(ak.stock_zh_a_spot_em)
        row = df[df["代码"] == pure_code]
        if row.empty:
            raise Exception(f"未找到股票: {code}")
        r = row.iloc[0]
        return RealtimeQuoteBean(
            code=code,
            name=r["名称"],
            price=float(r["最新价"]),
            change=float(r["涨跌额"]),
            change_pct=float(r["涨跌幅"]),
            volume=float(r["成交量"]),
            provider="akshare",
        )

    async def get_market_sentiment(self, date: str) -> MarketSentimentBean:
        """获取全市场情绪数据（东方财富实时行情）"""
        df = await self._fetch_with_retry(ak.stock_zh_a_spot_em)
        if df is None or df.empty:
            raise Exception("未获取到市场数据")

        # 过滤无效行（最新价为空或为 0）
        df = df[df["最新价"].notna() & (df["最新价"] > 0)]

        # 涨跌统计
        up_count = int((df["涨跌幅"] > 0).sum())
        down_count = int((df["涨跌幅"] < 0).sum())

        # 涨跌停统计（涨幅 >= 9.9% 视为涨停，跌幅 <= -9.9% 视为跌停）
        limit_up_count = int((df["涨跌幅"] >= 9.9).sum())
        limit_down_count = int((df["涨跌幅"] <= -9.9).sum())

        # 炸板率：涨幅在 5~9.9% 之间（曾涨停但未封板）占涨停数的比例
        near_limit_up = int(((df["涨跌幅"] >= 5) & (df["涨跌幅"] < 9.9)).sum())
        blow_rate = round(near_limit_up / limit_up_count * 100, 1) if limit_up_count > 0 else 0.0

        # 最高连板：用最高涨幅近似（真实连板数据需要历史数据支持）
        max_change_pct = float(df["涨跌幅"].max()) if not df.empty else 0.0
        max_streak = min(10, max(1, round(max_change_pct / 10)))

        # 总成交额（元）
        total_volume = float(df["成交额"].sum()) if "成交额" in df.columns else 0.0

        # 成交量相较昨日变化（%）：若数据源提供昨日成交额字段则计算
        volume_vs_yesterday = None
        if "成交额" in df.columns and "昨日成交额" in df.columns:
            yesterday_volume = float(df["昨日成交额"].sum())
            if yesterday_volume > 0:
                volume_vs_yesterday = round((total_volume - yesterday_volume) / yesterday_volume * 100, 2)

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
            volume_vs_yesterday=volume_vs_yesterday,
            avg_change_pct=float(df["涨跌幅"].mean()),
            max_change_pct=max_change_pct,
            provider="akshare",
        )
