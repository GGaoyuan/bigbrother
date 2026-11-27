"""按除权参考价计算前复权并缓存因子。"""

from bisect import bisect_right
from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import date, datetime
from fractions import Fraction
from hashlib import sha256

from app.core.cache import ExpiringCache
from app.core.exceptions import UnsupportedMarketData
from app.core.logger import log_provider, observe_provider
from app.core.market_time import CHINA, midnight
from app.models.model import Candle, CorporateAction
from app.models.provider import MarketDataProvider


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
            adjustment="qfq",
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


def build_qfq(actions: tuple[CorporateAction, ...], *, as_of: date, source: str) -> AdjustmentFactors:
    seen = set()
    by_day = defaultdict(list)
    for action in actions:
        day = action.ex_date
        cash, bonus, rights = action.cash_dividend, action.bonus_shares, action.rights_shares
        payment = rights * action.rights_price
        identity = (day, cash, bonus, rights, payment)
        if day <= as_of and (cash or bonus or rights) and identity not in seen:
            seen.add(identity)
            by_day[day].append((cash, bonus, rights, payment))

    daily_actions = []
    for event_day, values in sorted(by_day.items()):
        # 同一除权日的各项公告都以除权前每 10 股为计算基数。
        cash, bonus, rights, payment = (sum(column) for column in zip(*values))
        daily_actions.append((event_day, cash, bonus, rights, payment))

    scale, offset = Fraction(1), Fraction(0)
    transforms = [(scale, offset)]
    for _, cash, bonus, rights, payment in reversed(daily_actions):
        # 先应用当日的除权参考价公式，再叠加后续除权事件。
        # 除权参考价 P' =（10 × P − 现金红利 + 配股支付额）÷（10 + 送转股数 + 配股数）。
        denominator = 10 + bonus + rights
        offset += scale * (payment - cash) / denominator
        scale = scale * 10 / denominator
        transforms.append((scale, offset))

    canonical = "\n".join(",".join(str(value) for value in action) for action in daily_actions)
    digest = sha256(canonical.encode("ascii")).hexdigest()
    # 沿用现有前复权算法在 API 和缓存中的版本前缀。
    return AdjustmentFactors(
        version=f"tdx-affine-qfq-v1:{digest}",
        source=source,
        _action_days=tuple(action[0] for action in daily_actions),
        _transforms=tuple(reversed(transforms)),
    )


class AdjustmentService:
    def __init__(self, source: MarketDataProvider):
        self.source = source
        self.factor_cache = ExpiringCache(256)

    def get_factors(self, symbol: str) -> AdjustmentFactors:
        source = self.source
        as_of = datetime.now(CHINA).date()
        key = (source.name, source.version, symbol, as_of)
        factors = self.factor_cache.get(key)
        if factors is None:
            with observe_provider(source.name, "adjustment_factors", symbol=symbol, version=source.version):
                factors = build_qfq(source.get_corporate_actions(symbol), as_of=as_of, source=source.name)
            self.factor_cache.put(key, factors, 300)
        else:
            log_provider("cache_hit", source.name, "adjustment_factors", symbol=symbol, version=factors.version)
        return factors
