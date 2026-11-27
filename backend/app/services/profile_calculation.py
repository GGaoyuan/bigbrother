"""使用完整的 1 分钟 K 线估算成交量分布，按整数价格单位和股数计算。"""

from decimal import Decimal
from app.core.exceptions import UnsupportedMarketData
from app.models.model import Candle
from app.models.model import PriceLevel, ValueArea, VolumeDistribution


ALGORITHM_VERSION = "weighted-range-v1"
BUCKET_VERSION = "nice-step-120-v1"
VALUE_AREA_PERCENT = 70
TARGET_LEVELS = 120


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
