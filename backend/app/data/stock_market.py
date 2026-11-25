"""Serve validated data from one provider per result, with bounded in-memory caches."""

import hashlib
import hmac
import secrets
from collections import OrderedDict
from dataclasses import asdict
from datetime import datetime
from math import isfinite
from threading import Lock
from time import monotonic

from app.console_logging import log_provider, observe_provider
from app.data.stock_market_types import (
    CHINA, Candle, MarketDataError, MarketDataProvider, MinuteCoverageError, ProviderUnavailable,
    StockNotFound, TickCoverageError, TickDay, UnsupportedMarketData, midnight,
    stock_exchange,
)
from app.data.stock_minute_profile import (
    exchange_calendar, has_trading_minutes, minute_window, quality_report, validate_minutes,
)
from app.data.stock_volume_profile import ALGORITHM_VERSION, BUCKET_VERSION, calculate_profile, price_in_cents


MAX_RANGE_DAYS = 366
CURSOR_KEY = secrets.token_bytes(32)


class ExpiringCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = OrderedDict()
        self.lock = Lock()

    def get(self, key):
        with self.lock:
            entry = self.entries.get(key)
            if entry is None:
                return None
            expiry, value = entry
            if expiry <= monotonic():
                del self.entries[key]
                return None
            self.entries.move_to_end(key)
            return value

    def put(self, key, value, ttl):
        with self.lock:
            self.entries[key] = (monotonic() + ttl, value)
            self.entries.move_to_end(key)
            if len(self.entries) > self.capacity:
                self.entries.popitem(last=False)

    def keys(self):
        with self.lock:
            return tuple(self.entries)


def _sign_cursor(value: str) -> str:
    digest = hmac.digest(CURSOR_KEY, value.encode(), "sha256").hex()[:24]
    return f"{value}:{digest}"


def _validate_bars(bars, start, end, limit) -> tuple[Candle, ...]:
    by_time = {}
    for bar in bars:
        prices = (bar.open, bar.high, bar.low, bar.close)
        if (
            not all(isfinite(price) and price > 0 for price in prices)
            or not bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high
            or type(bar.volume) is not int or bar.volume < 0
            or (bar.amount is not None and (not isfinite(bar.amount) or bar.amount < 0))
            or not 0 <= bar.timestamp < bar.end_timestamp
        ):
            raise ProviderUnavailable("K 线包含非法时间、OHLC 或成交量")
        if ((start is not None and bar.end_timestamp <= start) or
                (end is not None and bar.timestamp >= end)):
            continue
        existing = by_time.get(bar.timestamp)
        if existing is not None and existing != bar:
            raise ProviderUnavailable("K 线包含冲突的重复时间")
        by_time[bar.timestamp] = bar
    ordered = tuple(by_time[key] for key in sorted(by_time)[-limit:])
    if not ordered:
        raise ProviderUnavailable("所请求区间无 K 线数据")
    if any(first.end_timestamp > second.timestamp for first, second in zip(ordered, ordered[1:])):
        raise ProviderUnavailable("K 线包含重叠时间区间")
    return ordered


def _validate_ticks(batch: TickDay, day):
    seen = set()
    previous = -1
    if batch.day != day:
        raise ProviderUnavailable("逐笔返回日期与请求不符")
    for tick in batch.ticks:
        if (
            tick.timestamp < previous
            or datetime.fromtimestamp(tick.timestamp, CHINA).date() != day
            or not isfinite(tick.price) or tick.price <= 0
            or type(tick.volume) is not int or tick.volume <= 0
            or (tick.amount is not None and (not isfinite(tick.amount) or tick.amount <= 0))
            or tick.side not in ("BUY", "SELL", "UNKNOWN")
            or (tick.trade_id is not None and tick.trade_id in seen)
        ):
            raise ProviderUnavailable("逐笔数据包含错误日期、字段或重复成交编号")
        previous = tick.timestamp
        if tick.trade_id is not None:
            seen.add(tick.trade_id)


class StockMarket:
    def __init__(self, providers: tuple[MarketDataProvider, ...], *, minute_providers=None, calendar_reader=exchange_calendar):
        self.providers = providers
        self.minute_providers = providers if minute_providers is None else minute_providers
        self.calendar_reader = calendar_reader
        self.calendar_cache = ExpiringCache(1)
        self.factor_cache = ExpiringCache(256)
        self.adjusted_cache = ExpiringCache(256)
        self.minute_cache = ExpiringCache(64)
        self.lookup_cache = ExpiringCache(256)
        self.history_cache = ExpiringCache(256)
        self.tick_cache = ExpiringCache(96)
        self.coverage_cache = ExpiringCache(128)
        self.profile_cache = ExpiringCache(64)

    def _fallback(self, label, symbol, reader, *, coverage=False, **parameters):
        failures = []
        for provider in self.providers:
            try:
                with observe_provider(provider.name, label, symbol=symbol, version=provider.version, **parameters):
                    return reader(provider)
            except MarketDataError as exc:
                failures.append((provider.name, exc))
        message = "；".join(f"{source}：{error}" for source, error in failures)
        if coverage:
            raise TickCoverageError(f"所选区间缺少可用于统计的完整真实逐笔数据。{message}")
        if any(isinstance(exc, StockNotFound) for _, exc in failures):
            if all(isinstance(exc, (StockNotFound, UnsupportedMarketData)) for _, exc in failures):
                raise StockNotFound(f"未找到股票 {symbol}。{message}")
        if all(isinstance(exc, UnsupportedMarketData) for _, exc in failures):
            raise UnsupportedMarketData(message)
        raise ProviderUnavailable(message or "无可用行情数据源")

    def stock(self, symbol):
        exchange = stock_exchange(symbol)

        def read(provider):
            key = (provider.name, provider.version, symbol)
            info = self.lookup_cache.get(key)
            if info is None:
                info = provider.get_stock_info(symbol)
                if info.symbol != symbol or info.exchange != exchange or not info.name.strip():
                    raise ProviderUnavailable("股票代码、交易所或名称校验失败")
                self.lookup_cache.put(key, info, 3600)
            else:
                log_provider("cache_hit", provider.name, "stock", symbol=symbol)
            available = [
                item.name for item in self.providers
                if self.lookup_cache.get((item.name, item.version, symbol)) is not None
            ]
            return {
                **asdict(info), "source": provider.name, "source_version": provider.version,
                "available_sources": available,
                "configured_sources": [item.name for item in self.providers],
            }

        return self._fallback("stock", symbol, read)

    def klines(self, symbol, interval, adjust, start, end, limit):
        stock_exchange(symbol)

        def read(provider):
            key = (provider.name, provider.version, symbol, interval, adjust, start, end, limit)
            bars = self.history_cache.get(key)
            if bars is None:
                bars = _validate_bars(
                    provider.get_klines(symbol, interval, adjust, start, end, limit),
                    start, end, limit,
                )
                historic = end is not None and end <= midnight(datetime.now(CHINA).date())
                self.history_cache.put(key, bars, 1800 if historic and adjust == "none" else 30)
            else:
                log_provider("cache_hit", provider.name, "klines", symbol=symbol, interval=interval)
            return {
                "symbol": symbol, "interval": interval, "adjust": adjust, "source": provider.name,
                "source_version": provider.version, "timezone": "Asia/Shanghai",
                "volume_unit": "shares", "bars": bars,
            }

        return self._fallback(
            "klines", symbol, read, interval=interval, adjust=adjust, start=start, end=end, limit=limit,
        )

    def _adjustment_factors(self, symbol):
        provider = self.providers[0]
        key = (provider.name, provider.version, symbol, datetime.now(CHINA).date())
        factors = self.factor_cache.get(key)
        if factors is None:
            with observe_provider(provider.name, "adjustment_factors", symbol=symbol, version=provider.version):
                factors = provider.get_adjustment_factors(symbol)
            self.factor_cache.put(key, factors, 300)
        else:
            log_provider("cache_hit", provider.name, "adjustment_factors", symbol=symbol, version=factors.version)
        return factors

    def chart_klines(self, symbol, interval, start, end, limit, cursor=None):
        if cursor is not None:
            end = cursor if end is None else min(end, cursor)
        if start is not None and end is not None and start >= end:
            raise UnsupportedMarketData("开始时间必须早于结束时间")

        raw_interval = "day" if interval == "1d" else interval
        raw = self.klines(symbol, raw_interval, "none", start, end, limit)
        factors = self._adjustment_factors(symbol)
        bars = raw["bars"]
        revision = hashlib.sha256(repr(bars).encode()).hexdigest()
        key = (symbol, interval, raw["source"], raw["source_version"], revision, factors.version)
        adjusted = self.adjusted_cache.get(key)
        if adjusted is None:
            adjusted = tuple(factors.apply(bar) for bar in bars)
            self.adjusted_cache.put(key, adjusted, 1800)

        oldest = adjusted[0].timestamp
        next_cursor = oldest if len(adjusted) == limit and (start is None or oldest > start) else None
        return {
            **raw, "interval": interval, "adjust": "qfq", "adjustment_version": factors.version,
            "adjustment_source": factors.source, "bars": adjusted, "next_cursor": next_cursor,
        }

    def _coverage_source(self, provider, symbol):
        key = (provider.name, provider.version, symbol)
        result = self.coverage_cache.get(key)
        if result is None:
            with observe_provider(provider.name, "tick_coverage", symbol=symbol, version=provider.version):
                result = provider.get_tick_coverage(symbol)
            self.coverage_cache.put(key, result, 30)
        else:
            log_provider("cache_hit", provider.name, "tick_coverage", symbol=symbol)
        return result

    def coverage(self, symbol):
        stock_exchange(symbol)
        sources = []
        for provider in self.providers:
            try:
                coverage = asdict(self._coverage_source(provider, symbol))
            except MarketDataError as exc:
                coverage = {
                    "start": None, "end": None, "complete": None, "history_supported": None,
                    "has_direction": None, "covers_bse": None, "resolution": None,
                    "reason": str(exc),
                }
            complete_dates, exact_dates = [], []
            for key in self.tick_cache.keys():
                if key[:3] != (provider.name, provider.version, symbol):
                    continue
                cached = self.tick_cache.get(key)
                if cached and cached[0].complete:
                    complete_dates.append(cached[0].day)
                    if cached[0].price_volume_exact:
                        exact_dates.append(cached[0].day)
            sources.append({
                **coverage, "source": provider.name, "source_version": provider.version,
                "continuous": False, "observed_complete_dates": sorted(complete_dates),
                "observed_exact_dates": sorted(exact_dates),
            })
        return {"symbol": symbol, "timezone": "Asia/Shanghai", "sources": sources}

    def _trading_days(self, symbol, start, end):
        last = datetime.fromtimestamp(end - 1, CHINA).date()
        first = datetime.fromtimestamp(start, CHINA).date()
        if last < first or (last - first).days >= MAX_RANGE_DAYS:
            raise UnsupportedMarketData(f"单次逐笔查询最多支持 {MAX_RANGE_DAYS} 个自然日")
        if last > datetime.now(CHINA).date():
            raise TickCoverageError("所选区间包含未来日期")
        # Include the entire final day; daily data establishes which dates have trades.
        data = self.klines(symbol, "day", "none", midnight(first), midnight(last) + 86400, MAX_RANGE_DAYS)
        days = tuple(
            datetime.fromtimestamp(bar.timestamp, CHINA).date()
            for bar in data["bars"] if bar.volume > 0
        )
        if not days:
            raise TickCoverageError("所选区间没有已知的交易日")
        return days, data["bars"]

    @staticmethod
    def _check_date(coverage, day):
        if (coverage.start and coverage.start > day) or (coverage.end and coverage.end < day):
            available = f"{coverage.start or '较早日期'} 至 {coverage.end or '最近日期'}"
            raise TickCoverageError(f"{day} 超出该源报告的范围（{available}）")

    def _load_day(self, provider, symbol, day):
        key = (provider.name, provider.version, symbol, day)
        cached = self.tick_cache.get(key)
        if cached is not None:
            log_provider("cache_hit", provider.name, "ticks", symbol=symbol, date=day)
            return cached
        self._check_date(self._coverage_source(provider, symbol), day)
        batch = provider.get_ticks(symbol, day)
        _validate_ticks(batch, day)
        if not batch.ticks:
            raise TickCoverageError(batch.reason or f"{day} 没有返回逐笔记录")
        fingerprint = hashlib.sha256(repr(batch).encode()).hexdigest()[:20]
        result = (batch, fingerprint)
        self.tick_cache.put(key, result, 10800 if batch.complete and day < datetime.now(CHINA).date() else 20)
        return result

    def ticks(self, symbol, start, end, limit, cursor):
        days, _ = self._trading_days(symbol, start, end)
        scope = hashlib.sha256(repr((symbol, start, end, days)).encode()).hexdigest()[:20]
        source = None
        day_index = offset = 0
        expected = "-"
        prior_verified = "1"
        if cursor:
            try:
                value, _ = cursor.rsplit(":", 1)
                if not cursor.isascii() or not hmac.compare_digest(_sign_cursor(value), cursor):
                    raise ValueError
                source, stored_scope, day_text, offset_text, expected, prior_verified = value.split(":")
                day_index, offset = int(day_text), int(offset_text)
                if (stored_scope != scope or not 0 <= day_index < len(days) or offset < 0
                        or (expected == "-" and offset != 0)):
                    raise ValueError
            except ValueError as exc:
                raise TickCoverageError("逐笔分页游标与当前查询区间不符") from exc

        def read(provider):
            day = days[day_index]
            batch, fingerprint = self._load_day(provider, symbol, day)
            version = hashlib.sha256(f"{provider.version}:{fingerprint}".encode()).hexdigest()[:20]
            if not batch.complete:
                raise TickCoverageError(batch.reason or f"{day} 的逐笔分页未通过完整性校验")
            if expected != "-" and expected != version:
                raise TickCoverageError("逐笔快照已变化，请从第一页重新查询")
            rows = tuple(tick for tick in batch.ticks if start <= tick.timestamp < end)
            requested_day_end = min(end, midnight(day) + 86400)
            day_complete = batch.verified_until is None or requested_day_end <= batch.verified_until
            if not rows and not day_complete:
                raise TickCoverageError(batch.reason or f"{day} 的所选时段没有可核验的成交记录")
            verified = "1" if day_complete and prior_verified == "1" else "0"
            if offset > len(rows):
                raise TickCoverageError("逐笔分页起点无效")
            page = rows[offset:offset + limit]
            if offset + limit < len(rows):
                next_cursor = _sign_cursor(f"{provider.name}:{scope}:{day_index}:{offset + limit}:{version}:{verified}")
            elif day_index + 1 < len(days):
                next_cursor = _sign_cursor(f"{provider.name}:{scope}:{day_index + 1}:0:-:{verified}")
            else:
                next_cursor = None
            return {
                "symbol": symbol, "source": provider.name, "source_version": provider.version,
                "start": start, "end": end, "date": day, "ticks": page,
                "complete": next_cursor is None and verified == "1", "day_complete": day_complete,
                "pagination_complete": next_cursor is None, "day_trade_count": len(rows),
                "verified_until": batch.verified_until,
                "resolution": batch.resolution, "price_volume_exact": batch.price_volume_exact,
                "original_volume_unit": batch.original_volume_unit, "volume_unit": "shares",
                "has_direction": any(tick.side != "UNKNOWN" for tick in rows),
                "timezone": "Asia/Shanghai", "next_cursor": next_cursor, "note": batch.reason,
                "omitted_zero_lot_rows": batch.omitted_zero_lot_rows,
            }

        if source:
            for provider in self.providers:
                if source == provider.name:
                    try:
                        with observe_provider(
                            provider.name, "ticks", symbol=symbol, version=provider.version,
                            date=days[day_index], pageOffset=offset, limit=limit, pinnedProvider=True,
                        ):
                            return read(provider)
                    except MarketDataError as exc:
                        raise TickCoverageError(f"分页源 {source} 无法继续。{exc}") from exc
            raise TickCoverageError("逐笔分页来源无效")
        return self._fallback(
            "ticks", symbol, read, coverage=True, start=start, end=end, limit=limit,
        )

    def _profile_sessions(self, start, end, quality):
        first = datetime.fromtimestamp(start, CHINA).date()
        last = datetime.fromtimestamp(end - 1, CHINA).date()
        if (last - first).days >= MAX_RANGE_DAYS:
            raise UnsupportedMarketData(f"单次分布计算最多支持 {MAX_RANGE_DAYS} 个自然日")
        if last > datetime.now(CHINA).date():
            raise MinuteCoverageError("所选区间包含未来交易日", quality)
        calendar = self.calendar_cache.get("sessions")
        if calendar is None:
            with observe_provider("akshare-sina", "exchange_calendar"):
                calendar = self.calendar_reader()
            self.calendar_cache.put("sessions", calendar, 21600)
        else:
            log_provider("cache_hit", "akshare-sina", "exchange_calendar")
        if not calendar or first < calendar[0] or last > calendar[-1]:
            raise MinuteCoverageError("交易日历未覆盖所选区间", quality)
        sessions = tuple(day for day in calendar if first <= day <= last)
        if not sessions or not has_trading_minutes(start, end, sessions):
            raise MinuteCoverageError("所选区间没有交易分钟", quality)
        return sessions

    def _minute_snapshot(self, provider, symbol, first, last):
        if getattr(provider, "minute_historical_queries", False) is True:
            start, end = midnight(first), midnight(last) + 86400
            limit = MAX_RANGE_DAYS * 240
        else:
            start, end = None, None
            limit = 320 if provider.name == "a-stock-data" else 3000
        key = (provider.name, provider.version, symbol, start, end)
        snapshot = self.minute_cache.get(key)
        if snapshot is None:
            acquired_at = datetime.now(CHINA)
            cutoff = int(acquired_at.timestamp()) // 60 * 60
            log_provider(
                "fetch", provider.name, "profile_minutes", symbol=symbol,
                interval="1m", adjust="none", start=start, end=end, limit=limit,
            )
            bars = provider.get_klines(symbol, "1m", "none", start, end, limit)
            snapshot = (bars, cutoff)
            if bars:
                ttl = 300 if acquired_at.hour >= 15 else min(45, cutoff + 60 - datetime.now(CHINA).timestamp())
                if ttl > 0:
                    self.minute_cache.put(key, snapshot, ttl)
        else:
            log_provider("cache_hit", provider.name, "profile_minutes", symbol=symbol)
        return snapshot

    def _profile_minutes(self, symbol, start, end, sessions, daily, quality):
        failures = []
        best_quality = quality
        requested = {"requested_start": quality["requested_start"], "requested_end": quality["requested_end"]}
        for provider in self.minute_providers:
            fields = {"symbol": symbol, "version": provider.version, "start": start, "end": end}
            log_provider("attempt", provider.name, "profile_minutes", **fields)
            try:
                snapshot, closed_until = self._minute_snapshot(provider, symbol, sessions[0], sessions[-1])
                bars, report = validate_minutes(
                    snapshot, start, end, sessions, daily, provider.name, closed_until=closed_until,
                )
            except MarketDataError as exc:
                failures.append({"source": provider.name, "message": str(exc)})
                log_provider(
                    "failed", provider.name, "profile_minutes", **fields,
                    errorType=type(exc).__name__, reason=str(exc),
                    dataQuality=exc.quality if isinstance(exc, MinuteCoverageError) else None,
                )
                if isinstance(exc, MinuteCoverageError):
                    candidate = exc.quality
                    has_better_coverage = (
                        candidate["minute_count"] > best_quality["minute_count"]
                        or (best_quality["available_start"] is None and candidate["available_start"] is not None)
                        or (best_quality["missing_minute_count"] is None and candidate["missing_minute_count"] is not None)
                    )
                    if has_better_coverage:
                        best_quality = {**candidate, **requested}
                continue
            log_provider(
                "selected", provider.name, "profile_minutes", **fields, rowCount=len(bars),
                availableStart=report["available_start"], availableEnd=report["available_end"],
                actualStart=report["actual_start"], actualEnd=report["actual_end"],
                totalShares=sum(bar.volume for bar in bars),
                volumePrecisionShares=report["volume_precision_shares"],
            )
            return bars, {**report, **requested}, provider.version

        best_quality["source_errors"] = failures
        message = "所选区间没有完整的 1 分钟 K 线"
        if best_quality["daily_mismatches"]:
            affected = "、".join(best_quality["daily_mismatches"][:3])
            message = f"分钟行情与对应日线的成交量或价格对账不一致（{affected}）"
        elif best_quality["duplicate_count"] or best_quality["invalid_count"]:
            message = "所选区间的 1 分钟 K 线含重复或异常记录"
        if best_quality["available_start"] is not None:
            available_start = datetime.fromtimestamp(best_quality["available_start"], CHINA)
            available_end = datetime.fromtimestamp(best_quality["available_end"], CHINA)
            message += f"。当前取得的分钟数据范围为 {available_start:%Y-%m-%d %H:%M} 至 {available_end:%Y-%m-%d %H:%M}"
        raise MinuteCoverageError(message, best_quality)

    def volume_profile(self, symbol, requested_start, requested_end):
        start, end = minute_window(requested_start, requested_end)
        quality = quality_report(start, end, None)
        quality.update(requested_start=requested_start, requested_end=requested_end)
        sessions = self._profile_sessions(start, end, quality)
        try:
            daily = self.klines(
                symbol, "day", "none", midnight(sessions[0]), midnight(sessions[-1]) + 86400,
                MAX_RANGE_DAYS,
            )["bars"]
        except MarketDataError as exc:
            raise MinuteCoverageError(f"缺少用于核验分钟行情的日线：{exc}", quality) from exc

        bars, quality, source_version = self._profile_minutes(symbol, start, end, sessions, daily, quality)
        try:
            factors = self._adjustment_factors(symbol)
            tick_cents = price_in_cents(self.stock(symbol)["price_tick"])
        except MarketDataError as exc:
            quality["complete"] = False
            raise MinuteCoverageError(f"无法核验前复权因子或行情价格精度：{exc}", quality) from exc

        revision = hashlib.sha256(repr(bars).encode()).hexdigest()
        key = (
            symbol, start, end, quality["source"], source_version, revision, factors.version,
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
            log_provider("cache_hit", quality["source"], "volume_profile", symbol=symbol, start=start, end=end)

        step, profile = result
        quality["factor_complete"] = True
        if not profile["total"]:
            quality["complete"] = False
            raise MinuteCoverageError("所选交易分钟没有成交量", quality)
        source = quality["source"]
        warnings = ["按完整的 1 分钟 K 线估算，无法区分逐笔成交方向"]
        if quality["volume_precision_shares"] > 1:
            warnings.append(f"该行情源按 {quality['volume_precision_shares']} 股粒度公布分钟成交量")
        return {
            "symbol": symbol, "start": requested_start, "end": requested_end,
            "actual_start": quality["actual_start"], "actual_end": quality["actual_end"],
            "calculation_method": "estimated_1m_weighted_range",
            "source": source, "data_source": source, "source_version": source_version,
            "data_version": revision, "adjustment_version": factors.version,
            "adjustment_source": factors.source, "adjust": "qfq", "volume_unit": "shares",
            "price_step": step / 100, "total_volume": profile["total"],
            "price_levels": profile["levels"], "poc": profile["poc"]["priceCents"] / 100,
            "vah": profile["valueArea"]["high"] / 100, "val": profile["valueArea"]["low"] / 100,
            "profile": profile, "complete": True, "data_quality": quality,
            "warnings": warnings,
        }
