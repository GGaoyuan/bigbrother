"""获取前复权分钟行情、检查覆盖并估算固定区间成交量分布。"""

import hashlib
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from math import isfinite
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.core.exceptions import MarketDataError, ProviderUnavailable, UnsupportedMarketData
from app.core.logger import log_provider, observe_provider
from app.core.market_time import CHINA, has_trading_minutes, market_at, midnight, minute_window, required_minutes
from app.core.response import ApiResponse, success_response
from app.models.calendar.provider import TradingCalendarProvider
from app.models.kline.model import Candle
from app.models.volume_profile.model import MinuteQuality, PriceLevel, ValueArea, VolumeDistribution, VolumeProfileResult

from . import kline, stock
from ._shared import MAX_TIMESTAMP, Symbol


router = APIRouter()
_calendar_provider = TradingCalendarProvider()

MAX_RANGE_DAYS = 366
VALUE_AREA_PERCENT = 70
TARGET_LEVELS = 120


class ProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: int = Field(ge=0, le=MAX_TIMESTAMP)
    end: int = Field(ge=0, le=MAX_TIMESTAMP)


class LevelResponse(BaseModel):
    priceCents: int
    lowPriceCents: int
    highPriceCents: int
    total: int
    buy: Literal[0] = 0
    sell: Literal[0] = 0
    neutral: Literal[0] = 0
    unknown: int
    delta: None = None
    node: Literal["HVN", "LVN"] | None


class ValueAreaResponse(BaseModel):
    low: int
    high: int
    volume: int


class DistributionResponse(BaseModel):
    levels: tuple[LevelResponse, ...]
    poc: LevelResponse
    total: int
    valueArea: ValueAreaResponse
    hasDirection: Literal[False] = False


class ProfileResponse(BaseModel):
    symbol: str
    start: int
    end: int
    actual_start: int
    actual_end: int
    calculation_method: Literal["estimated_1m_weighted_range"] = "estimated_1m_weighted_range"
    source: str
    data_source: str
    source_version: str
    data_version: str
    adjustment_version: str
    adjustment_source: str
    adjust: Literal["qfq"] = "qfq"
    volume_unit: Literal["shares"] = "shares"
    price_step: float
    total_volume: int
    price_levels: tuple[LevelResponse, ...]
    poc: float
    vah: float
    val: float
    profile: DistributionResponse
    complete: Literal[True] = True
    data_quality: dict[str, object]
    warnings: list[str]


@router.post(
    "/{symbol}/volume-profile",
    response_model=ApiResponse[ProfileResponse],
    summary="基于 1 分钟 K 线估算价位分布",
)
def volume_profile(symbol: Symbol, body: ProfileRequest) -> ApiResponse[ProfileResponse]:
    return success_response(_profile_response(symbol, get_volume_profile(symbol, body.start, body.end)))


class MinuteCoverageError(MarketDataError):
    def __init__(self, message: str, quality: MinuteQuality):
        super().__init__(message)
        self.quality = quality


def _valid(bar: Candle, day: Candle | None) -> bool:
    if (
        day is None or bar.adjustment != "qfq" or day.adjustment != "qfq"
        or bar.timestamp % 60 or bar.end_timestamp != bar.timestamp + 60
        or not kline.has_valid_ohlcv(bar)
        or bar.volume_precision_shares not in (1, 100) or bar.volume % bar.volume_precision_shares
        or bar.original_volume_unit not in ("lots", "shares")
        or bar.original_volume is None or not isfinite(bar.original_volume) or bar.original_volume < 0
        or bar.low < day.low - 0.0101 or bar.high > day.high + 0.0101
    ):
        return False
    multiplier = 100 if bar.original_volume_unit == "lots" else 1
    if Decimal(str(bar.original_volume)) * multiplier != bar.volume:
        return False
    # 成交额按原价统计，不能与前复权价格直接比较。
    return bar.amount is None or (bar.amount == 0) == (bar.volume == 0)


def quality_report(start: int, end: int, source: str | None) -> MinuteQuality:
    return {
        "requested_start": start, "requested_end": end,
        "aligned_start": start, "aligned_end": end,
        "actual_start": None, "actual_end": None, "available_start": None, "available_end": None,
        "trading_day_count": 0, "minute_count": 0, "duplicate_count": 0, "invalid_count": 0,
        "missing_minute_count": None, "missing": [], "daily_mismatches": [], "source": source,
        "factor_complete": False, "complete": False, "volume_precision_shares": None,
    }


def validate_minutes(
    bars: tuple[Candle, ...], start: int, end: int, sessions: tuple[date, ...],
    daily_bars: tuple[Candle, ...], source: str,
) -> tuple[tuple[Candle, ...], MinuteQuality]:
    quality = quality_report(start, end, source)
    reference = {datetime.fromtimestamp(bar.timestamp, CHINA).date(): bar for bar in daily_bars}
    expected, optional = {}, set()
    for day in sessions:
        for regular in required_minutes(day):
            expected.update((stamp, day) for stamp in regular if start <= stamp < end)
        optional.update(
            stamp for stamp in (market_at(day, 14, 57), market_at(day, 14, 58)) if start <= stamp < end
        )

    if bars:
        quality["available_start"] = min(bar.timestamp for bar in bars)
        quality["available_end"] = max(bar.end_timestamp for bar in bars)
    if not expected:
        raise MinuteCoverageError("所选区间没有交易分钟", quality)

    selected: dict[int, Candle] = {}
    seen = set()
    for bar in bars:
        stamp = bar.timestamp
        if not start <= stamp < end:
            continue
        if stamp in seen:
            quality["duplicate_count"] += 1
            continue
        seen.add(stamp)
        day = datetime.fromtimestamp(stamp, CHINA).date()
        if (stamp not in expected and stamp not in optional) or not _valid(bar, reference.get(day)):
            quality["invalid_count"] += 1
            continue
        selected[stamp] = bar

    missing_by_day: dict[date, list[int]] = {}
    for stamp, day in expected.items():
        if stamp not in selected:
            missing_by_day.setdefault(day, []).append(stamp)
    rows = tuple(selected[stamp] for stamp in sorted(selected))
    if rows:
        quality["actual_start"] = rows[0].timestamp
        quality["actual_end"] = rows[-1].end_timestamp
    quality["missing"] = [
        {
            "date": day.isoformat(), "count": len(stamps), "first": stamps[0], "last": stamps[-1],
            "daily_reference_missing": day not in reference,
        }
        for day, stamps in missing_by_day.items()
    ]
    quality["minute_count"] = len(rows)
    if rows:
        quality["volume_precision_shares"] = max(bar.volume_precision_shares for bar in rows)
    quality["trading_day_count"] = len({datetime.fromtimestamp(bar.timestamp, CHINA).date() for bar in rows})
    quality["missing_minute_count"] = sum(len(stamps) for stamps in missing_by_day.values())
    if quality["duplicate_count"] or quality["invalid_count"] or quality["missing_minute_count"]:
        raise MinuteCoverageError(
            "所选区间的 1 分钟 K 线不足或未通过质量核验", quality,
        )
    by_day = defaultdict(list)
    for bar in rows:
        by_day[datetime.fromtimestamp(bar.timestamp, CHINA).date()].append(bar)
    for day, day_rows in by_day.items():
        if start > market_at(day, 9, 30) or end < market_at(day, 15, 0):
            continue
        daily = reference[day]
        volume = sum(bar.volume for bar in day_rows)
        tolerance = max(bar.volume_precision_shares for bar in day_rows) - 1
        if daily.original_volume_unit in ("lots", "rounded_lots"):
            tolerance = max(tolerance, 99)
        day_prices = (day_rows[0].open, max(bar.high for bar in day_rows),
                      min(bar.low for bar in day_rows), day_rows[-1].close)
        reference_prices = (daily.open, daily.high, daily.low, daily.close)
        if abs(volume - daily.volume) > tolerance or any(
            abs(given - expected) > 0.0101 for given, expected in zip(day_prices, reference_prices)
        ):
            quality["daily_mismatches"].append(day.isoformat())
    if quality["daily_mismatches"]:
        raise MinuteCoverageError("整日分钟 K 线的股数或价格与同源前复权日线不符", quality)
    quality["complete"] = True
    return rows, quality


def price_in_cents(price: float | Decimal) -> int:
    cents = Decimal(str(price)) * 100
    if not cents.is_finite() or cents <= 0 or cents != cents.to_integral_value():
        raise UnsupportedMarketData("价格必须是 0.01 元的正整数倍")
    return int(cents)


def _bucket_step(tick_count: int) -> int:
    minimum = (tick_count + TARGET_LEVELS - 1) // TARGET_LEVELS
    scale = 10 ** (len(str(minimum)) - 1)
    return next(value * scale for value in (1, 2, 5, 10) if value * scale >= minimum)


def _allocate(
    totals: list[int], low: int, high: int, close: int, volume: int, origin: int, step: int,
):
    first, last = (low - origin) // step, (high - origin) // step
    if first == last:
        totals[first] += volume
        return

    # p 取价格档与该分钟价格区间相交部分的中点。以最小价格单位的六分之一
    # 比较 p 与 (H + L + C) / 3，成交量仅分配到该分钟的价格区间内。
    span = max(high - low, 1)
    typical = high + low + close
    weights = []
    for index in range(first, last + 1):
        band_low = origin + index * step
        left, right = max(low, band_low), min(high, band_low + step - 1)
        distance = abs(3 * (left + right) - 2 * typical)
        weights.append(max(6 * span, 600 * span - 100 * distance))

    denominator = sum(weights)
    shares = [divmod(volume * weight, denominator) for weight in weights]
    remaining = volume - sum(whole for whole, _ in shares)
    for offset, (whole, _) in enumerate(shares):
        totals[first + offset] += whole
    # 按余数从大到小补齐，确保每分钟分配后的总股数等于原始值。
    for offset in sorted(range(len(shares)), key=lambda i: (-shares[i][1], -weights[i], i))[:remaining]:
        totals[first + offset] += 1


def _value_area(levels: list[PriceLevel], anchor: int, total: int) -> ValueArea:
    upper = lower = anchor
    volume = levels[anchor].volume
    target = total * VALUE_AREA_PERCENT
    while volume * 100 < target:
        above = levels[upper - 1].volume if upper > 0 else -1
        below = levels[lower + 1].volume if lower + 1 < len(levels) else -1
        if above > below or (above == below and anchor - upper <= lower - anchor):
            upper -= 1
            volume += above
        else:
            lower += 1
            volume += below
    return ValueArea(levels[lower].low_price_cents, levels[upper].high_price_cents, volume)


def calculate_profile(candles: tuple[Candle, ...], tick_cents: int = 1) -> VolumeDistribution:
    converted = []
    for candle in candles:
        prices = (price_in_cents(candle.low), price_in_cents(candle.high), price_in_cents(candle.close))
        if any(price % tick_cents for price in prices):
            raise UnsupportedMarketData("分钟 K 线价格与最小价格变动单位不一致")
        low, high, close = (price // tick_cents for price in prices)
        converted.append((low, high, close, candle.volume))
    if not any(row[3] > 0 for row in converted):
        return VolumeDistribution(tick_cents, (), 0)

    low, high = min(row[0] for row in converted), max(row[1] for row in converted)
    step = _bucket_step(high - low + 1)
    totals = [0] * ((high - low) // step + 1)
    for bar_low, bar_high, close, volume in converted:
        if volume:
            _allocate(totals, bar_low, bar_high, close, volume, low, step)

    total = sum(totals)
    levels: list[PriceLevel] = []
    for index, volume in enumerate(totals):
        band_low = low + index * step
        band_high = min(high, band_low + step - 1)
        node = None
        if volume > 0 and 0 < index < len(totals) - 1:
            neighbors = (totals[index - 1], totals[index + 1])
            if volume > max(neighbors) and volume * len(totals) >= total:
                node = "HVN"
            elif volume < min(neighbors) and volume * len(totals) <= total:
                node = "LVN"
        levels.append(PriceLevel(
            price_cents=(band_low + band_high + 1) // 2 * tick_cents,
            low_price_cents=band_low * tick_cents,
            high_price_cents=band_high * tick_cents,
            volume=volume,
            node=node,
        ))

    levels.reverse()
    anchor = max(range(len(levels)), key=lambda index: levels[index].volume)
    return VolumeDistribution(
        step_cents=step * tick_cents,
        levels=tuple(levels),
        total_volume=total,
        poc=levels[anchor],
        value_area=_value_area(levels, anchor, total),
    )


def _profile_sessions(start: int, end: int, quality: MinuteQuality) -> tuple[date, ...]:
    first = datetime.fromtimestamp(start, CHINA).date()
    last = datetime.fromtimestamp(end - 1, CHINA).date()
    if (last - first).days >= MAX_RANGE_DAYS:
        raise UnsupportedMarketData(f"单次分布计算最多支持 {MAX_RANGE_DAYS} 个自然日")
    if last > datetime.now(CHINA).date():
        raise MinuteCoverageError("所选区间包含未来交易日", quality)
    source = _calendar_provider
    with observe_provider(source.name, "exchange_calendar", version=source.version):
        calendar = source.get_calendar()
        if not calendar.sessions or calendar.sessions != tuple(sorted(set(calendar.sessions))):
            raise ProviderUnavailable("交易日历返回日期无效")
    if first < calendar.start or last > calendar.end:
        raise MinuteCoverageError("交易日历未覆盖所选区间", quality)
    sessions = tuple(day for day in calendar.sessions if first <= day <= last)
    if not sessions or not has_trading_minutes(start, end, sessions):
        raise MinuteCoverageError("所选区间没有交易分钟", quality)
    return sessions


def _profile_minutes(
    symbol: str, start: int, end: int, sessions: tuple[date, ...],
    daily: tuple[Candle, ...], quality: MinuteQuality,
) -> tuple[tuple[Candle, ...], MinuteQuality]:
    source = kline.provider
    requested = {"requested_start": quality["requested_start"], "requested_end": quality["requested_end"]}
    fields = {"symbol": symbol, "version": source.version, "start": start, "end": end}
    log_provider("attempt", source.name, "profile_minutes", **fields)
    try:
        day_start = midnight(sessions[0])
        day_end = midnight(sessions[-1]) + 86400
        limit = MAX_RANGE_DAYS * 240
        # 日线选区可包含今天的收盘，盘中只统计抓取时已经结束的整分钟。
        closed_until = int(datetime.now(CHINA).timestamp()) // 60 * 60
        log_provider(
            "fetch", source.name, "profile_minutes", symbol=symbol,
            interval="1m", adjust="qfq", start=day_start, end=day_end, limit=limit,
        )
        snapshot = source.get_klines(symbol, "1m", "qfq", day_start, day_end, limit)
        effective_end = max(start, min(end, closed_until))
        bars, report = validate_minutes(
            snapshot, start, effective_end, sessions, daily, source.name,
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


def get_volume_profile(symbol: str, requested_start: int, requested_end: int) -> VolumeProfileResult:
    if requested_start >= requested_end:
        raise UnsupportedMarketData("开始时间必须早于结束时间")
    start, end = minute_window(requested_start, requested_end)
    quality = quality_report(start, end, None)
    quality.update(requested_start=requested_start, requested_end=requested_end)
    sessions = _profile_sessions(start, end, quality)
    try:
        daily = kline.get_history(
            symbol, "1d", midnight(sessions[0]), midnight(sessions[-1]) + 86400,
            MAX_RANGE_DAYS,
        )
    except MarketDataError as exc:
        raise MinuteCoverageError(f"缺少用于核验分钟行情的日线：{exc}", quality) from exc

    bars, quality = _profile_minutes(symbol, start, end, sessions, daily.bars, quality)
    source = kline.provider
    try:
        tick_cents = price_in_cents(stock.get_stock(symbol).price_tick)
    except MarketDataError as exc:
        quality["complete"] = False
        raise MinuteCoverageError(f"无法核验行情价格精度：{exc}", quality) from exc

    try:
        result = calculate_profile(bars, tick_cents)
    except MarketDataError as exc:
        quality["complete"] = False
        raise MinuteCoverageError(str(exc), quality) from exc

    quality["factor_complete"] = True
    if not result.total_volume:
        quality["complete"] = False
        raise MinuteCoverageError("所选交易分钟没有成交量", quality)
    revision = hashlib.sha256(repr(bars).encode()).hexdigest()
    return VolumeProfileResult(
        result, quality, source.name, source.version, revision, daily.adjustment_version, source.name,
    )


def _level_response(level: PriceLevel) -> LevelResponse:
    return LevelResponse(
        priceCents=level.price_cents,
        lowPriceCents=level.low_price_cents,
        highPriceCents=level.high_price_cents,
        total=level.volume,
        unknown=level.volume,
        node=level.node,
    )


def _profile_response(symbol: str, result: VolumeProfileResult) -> ProfileResponse:
    distribution, quality = result.distribution, result.quality
    poc, area = distribution.poc, distribution.value_area
    actual_start, actual_end = quality["actual_start"], quality["actual_end"]
    assert poc is not None and area is not None and actual_start is not None and actual_end is not None
    levels = tuple(_level_response(level) for level in distribution.levels)
    warnings = ["按完整的 1 分钟 K 线估算，无法区分逐笔成交方向"]
    precision = quality["volume_precision_shares"]
    if precision is not None and precision > 1:
        warnings.append(f"该行情源按 {precision} 股粒度公布分钟成交量")
    return ProfileResponse(
        symbol=symbol,
        start=quality["requested_start"],
        end=quality["requested_end"],
        actual_start=actual_start,
        actual_end=actual_end,
        source=result.source,
        data_source=result.source,
        source_version=result.source_version,
        data_version=result.data_version,
        adjustment_version=result.adjustment_version,
        adjustment_source=result.adjustment_source,
        price_step=distribution.step_cents / 100,
        total_volume=distribution.total_volume,
        price_levels=levels,
        poc=poc.price_cents / 100,
        vah=area.high_cents / 100,
        val=area.low_cents / 100,
        profile=DistributionResponse(
            levels=levels,
            poc=_level_response(poc),
            total=distribution.total_volume,
            valueArea=ValueAreaResponse(low=area.low_cents, high=area.high_cents, volume=area.volume),
        ),
        data_quality=dict(quality),
        warnings=warnings,
    )
