"""Reference-price forward adjustment from Tongdaxin corporate actions."""

from bisect import bisect_right
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import date, datetime
from fractions import Fraction
from hashlib import sha256
from math import isfinite

from app.data.stock_market_types import CHINA, Candle, ProviderUnavailable, UnsupportedMarketData, midnight


@dataclass(frozen=True, slots=True)
class AdjustmentFactors:
    version: str
    source: str
    _action_days: tuple[date, ...]
    _transforms: tuple[tuple[Fraction, Fraction], ...]

    def apply(self, candle: Candle) -> Candle:
        candle_day = datetime.fromtimestamp(candle.timestamp, CHINA).date()
        index = bisect_right(self._action_days, candle_day)
        if index < len(self._action_days) and midnight(self._action_days[index]) < candle.end_timestamp:
            raise UnsupportedMarketData("跨除权除息日的 K 线须先按交易日复权再合成")

        scale, offset = self._transforms[index]
        return replace(
            candle,
            open=_chart_price(candle.open, scale, offset),
            high=_chart_price(candle.high, scale, offset),
            low=_chart_price(candle.low, scale, offset),
            close=_chart_price(candle.close, scale, offset),
        )


def _chart_price(price: float, scale: Fraction, offset: Fraction) -> float:
    adjusted = Fraction(str(price)) * scale + offset
    cents, remainder = divmod(adjusted.numerator * 100, adjusted.denominator)
    cents += int(2 * remainder >= adjusted.denominator)
    if cents <= 0:
        raise UnsupportedMarketData("该区间的前复权价格出现非正数，无法绘制")
    return cents / 100


def _action_value(row: Mapping, field: str) -> Fraction:
    value = row[field]
    if type(value) not in (int, float) or not isfinite(value) or value < 0:
        raise ValueError(field)
    return Fraction(str(value))


def build_tdx_qfq(rows: object, *, as_of: date) -> AdjustmentFactors:
    # tdxpy also decodes a short response body as an empty list. Only accept
    # identity factors after reading a valid corporate-action payload.
    if not isinstance(rows, (list, tuple)) or not rows:
        raise ProviderUnavailable("通达信未返回可核验的除权除息记录")

    seen = set()
    by_day = defaultdict(list)
    try:
        for row in rows:
            if not isinstance(row, Mapping) or type(row.get("category")) is not int or row["category"] < 1:
                raise ValueError("category")
            event_day = date(row["year"], row["month"], row["day"])
            if row["category"] != 1:
                continue
            cash, bonus, rights, rights_price = (
                _action_value(row, field) for field in ("fenhong", "songzhuangu", "peigu", "peigujia")
            )
            payment = rights * rights_price
            action = (event_day, cash, bonus, rights, payment)
            if event_day <= as_of and (cash or bonus or rights) and action not in seen:
                seen.add(action)
                by_day[event_day].append((cash, bonus, rights, payment))
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ProviderUnavailable("通达信除权除息记录格式异常") from exc

    actions = []
    for event_day, values in sorted(by_day.items()):
        # Notices for one ex-date use the same base of ten pre-action shares.
        cash, bonus, rights, payment = (sum(column) for column in zip(*values))
        actions.append((event_day, cash, bonus, rights, payment))

    scale, offset = Fraction(1), Fraction(0)
    transforms = [(scale, offset)]
    for _, cash, bonus, rights, payment in reversed(actions):
        # Apply this day's reference-price transform before all later actions.
        # P' = (10 * P - cash + rights payment) / (10 + bonus + rights).
        denominator = 10 + bonus + rights
        offset += scale * (payment - cash) / denominator
        scale = scale * 10 / denominator
        transforms.append((scale, offset))

    canonical = "\n".join(",".join(str(value) for value in action) for action in actions)
    digest = sha256(canonical.encode("ascii")).hexdigest()
    return AdjustmentFactors(
        version=f"tdx-affine-qfq-v1:{digest}",
        source="mootdx",
        _action_days=tuple(action[0] for action in actions),
        _transforms=tuple(reversed(transforms)),
    )
