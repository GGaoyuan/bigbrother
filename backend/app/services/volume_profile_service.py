"""检查成交量分布所需的数据覆盖，统一前复权并执行模式 B 估算。"""

import hashlib
from datetime import date, datetime

from app.core.cache import ExpiringCache
from app.core.exceptions import MarketDataError, ProviderUnavailable, UnsupportedMarketData
from app.core.logger import log_provider, observe_provider
from app.core.market_time import CHINA, has_trading_minutes, midnight, minute_window
from app.models.model import Candle, MinuteQuality, VolumeProfileResult

from .adjustment_service import AdjustmentService
from .kline_service import KlineService
from .minute_quality import MinuteCoverageError, quality_report, validate_minutes
from .profile_calculation import ALGORITHM_VERSION, BUCKET_VERSION, calculate_profile, price_in_cents
from .stock_service import StockInfoService


MAX_RANGE_DAYS = 366


class VolumeProfileService:
    def __init__(
        self, klines: KlineService, stocks: StockInfoService, adjustment: AdjustmentService,
    ):
        self.klines = klines
        self.stocks = stocks
        self.adjustment = adjustment
        self.calendar_cache = ExpiringCache(1)
        self.minute_cache = ExpiringCache(64)
        self.profile_cache = ExpiringCache(64)

    def _profile_sessions(self, start: int, end: int, quality: MinuteQuality) -> tuple[date, ...]:
        first = datetime.fromtimestamp(start, CHINA).date()
        last = datetime.fromtimestamp(end - 1, CHINA).date()
        if (last - first).days >= MAX_RANGE_DAYS:
            raise UnsupportedMarketData(f"单次分布计算最多支持 {MAX_RANGE_DAYS} 个自然日")
        if last > datetime.now(CHINA).date():
            raise MinuteCoverageError("所选区间包含未来交易日", quality)
        source = self.klines.source
        calendar_key = (source.calendar_name, source.calendar_version)
        calendar = self.calendar_cache.get(calendar_key)
        if calendar is None:
            with observe_provider(source.calendar_name, "exchange_calendar", version=source.calendar_version):
                calendar = source.get_calendar()
                if not calendar.sessions or calendar.sessions != tuple(sorted(set(calendar.sessions))):
                    raise ProviderUnavailable("交易日历返回日期无效")
            self.calendar_cache.put(calendar_key, calendar, 21600)
        else:
            log_provider("cache_hit", source.calendar_name, "exchange_calendar")
        if first < calendar.start or last > calendar.end:
            raise MinuteCoverageError("交易日历未覆盖所选区间", quality)
        sessions = tuple(day for day in calendar.sessions if first <= day <= last)
        if not sessions or not has_trading_minutes(start, end, sessions):
            raise MinuteCoverageError("所选区间没有交易分钟", quality)
        return sessions

    def _minute_snapshot(
        self, symbol: str, first: date, last: date,
    ) -> tuple[tuple[Candle, ...], int]:
        source = self.klines.source
        start, end = midnight(first), midnight(last) + 86400
        limit = MAX_RANGE_DAYS * 240
        key = (source.name, source.version, symbol, "1m", "none", start, end, limit)
        snapshot = self.minute_cache.get(key)
        if snapshot is None:
            acquired_at = datetime.now(CHINA)
            cutoff = int(acquired_at.timestamp()) // 60 * 60
            log_provider(
                "fetch", source.name, "profile_minutes", symbol=symbol,
                interval="1m", adjust="none", start=start, end=end, limit=limit,
            )
            bars = source.get_klines(symbol, "1m", "none", start, end, limit)
            snapshot = (bars, cutoff)
            if bars:
                ttl = 300 if acquired_at.hour >= 15 else min(45, cutoff + 60 - datetime.now(CHINA).timestamp())
                if ttl > 0:
                    self.minute_cache.put(key, snapshot, ttl)
        else:
            log_provider("cache_hit", source.name, "profile_minutes", symbol=symbol)
        return snapshot

    def _profile_minutes(
        self, symbol: str, start: int, end: int, sessions: tuple[date, ...],
        daily: tuple[Candle, ...], quality: MinuteQuality,
    ) -> tuple[tuple[Candle, ...], MinuteQuality]:
        source = self.klines.source
        requested = {"requested_start": quality["requested_start"], "requested_end": quality["requested_end"]}
        fields = {"symbol": symbol, "version": source.version, "start": start, "end": end}
        log_provider("attempt", source.name, "profile_minutes", **fields)
        try:
            snapshot, closed_until = self._minute_snapshot(symbol, sessions[0], sessions[-1])
            bars, report = validate_minutes(
                snapshot, start, end, sessions, daily, source.name, closed_until=closed_until,
            )
        except MarketDataError as exc:
            log_provider(
                "failed", source.name, "profile_minutes", **fields,
                errorType=type(exc).__name__, reason=str(exc),
                dataQuality=exc.quality if isinstance(exc, MinuteCoverageError) else None,
            )
            if isinstance(exc, MinuteCoverageError):
                quality = {**exc.quality, **requested}
            quality["source_errors"] = [{"source": source.name, "message": str(exc)}]
            message = "所选区间没有完整的 1 分钟 K 线"
            if quality["daily_mismatches"]:
                affected = "、".join(quality["daily_mismatches"][:3])
                message = f"分钟行情与对应日线的成交量或价格对账不一致（{affected}）"
            elif quality["duplicate_count"] or quality["invalid_count"]:
                message = "所选区间的 1 分钟 K 线含重复或异常记录"
            if quality["available_start"] is not None and quality["available_end"] is not None:
                available_start = datetime.fromtimestamp(quality["available_start"], CHINA)
                available_end = datetime.fromtimestamp(quality["available_end"], CHINA)
                message += f"。当前取得的分钟数据范围为 {available_start:%Y-%m-%d %H:%M} 至 {available_end:%Y-%m-%d %H:%M}"
            raise MinuteCoverageError(message, quality) from exc

        log_provider(
            "selected", source.name, "profile_minutes", **fields, rowCount=len(bars),
            availableStart=report["available_start"], availableEnd=report["available_end"],
            actualStart=report["actual_start"], actualEnd=report["actual_end"],
            totalShares=sum(bar.volume for bar in bars),
            volumePrecisionShares=report["volume_precision_shares"],
        )
        return bars, {**report, **requested}

    def calculate(self, symbol: str, requested_start: int, requested_end: int) -> VolumeProfileResult:
        if requested_start >= requested_end:
            raise UnsupportedMarketData("开始时间必须早于结束时间")
        start, end = minute_window(requested_start, requested_end)
        quality = quality_report(start, end, None)
        quality.update(requested_start=requested_start, requested_end=requested_end)
        sessions = self._profile_sessions(start, end, quality)
        try:
            daily = self.klines.get_history(
                symbol, "day", "none", midnight(sessions[0]), midnight(sessions[-1]) + 86400,
                MAX_RANGE_DAYS,
            ).bars
        except MarketDataError as exc:
            raise MinuteCoverageError(f"缺少用于核验分钟行情的日线：{exc}", quality) from exc

        bars, quality = self._profile_minutes(symbol, start, end, sessions, daily, quality)
        source = self.klines.source
        try:
            factors = self.adjustment.get_factors(symbol)
            tick_cents = price_in_cents(self.stocks.get_stock(symbol).stock.price_tick)
        except MarketDataError as exc:
            quality["complete"] = False
            raise MinuteCoverageError(f"无法核验前复权因子或行情价格精度：{exc}", quality) from exc

        revision = hashlib.sha256(repr(bars).encode()).hexdigest()
        key = (
            symbol, start, end, source.name, source.version, revision, factors.version,
            tick_cents, ALGORITHM_VERSION, BUCKET_VERSION,
        )
        result = self.profile_cache.get(key)
        if result is None:
            try:
                adjusted = tuple(factors.apply(bar) for bar in bars)
                result = calculate_profile(adjusted, tick_cents)
            except MarketDataError as exc:
                quality["complete"] = False
                raise MinuteCoverageError(str(exc), quality) from exc
            self.profile_cache.put(key, result, 600)
        else:
            log_provider("cache_hit", source.name, "volume_profile", symbol=symbol, start=start, end=end)

        quality["factor_complete"] = True
        if not result.total_volume:
            quality["complete"] = False
            raise MinuteCoverageError("所选交易分钟没有成交量", quality)
        return VolumeProfileResult(
            result, quality, source.name, source.version, revision, factors.version, factors.source,
        )
