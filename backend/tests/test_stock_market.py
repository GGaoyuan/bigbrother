from datetime import date, datetime
from time import monotonic
from unittest import TestCase
from unittest.mock import Mock, patch

from fractions import Fraction
from types import SimpleNamespace

from app.core.exceptions import ProviderUnavailable, StockNotFound
from app.core.market_time import CHINA, midnight
from app.models.calendar import TradingCalendar
from app.models.corporate_action import CorporateAction
from app.models.kline import Candle
from app.models.stock import StockInfo
from app.services.adjustment import AdjustmentService
from app.services.klines import KlineService
from app.services.minute_quality import MinuteCoverageError
from app.services.stock_info import StockInfoService
from app.services.volume_profile import VolumeProfileService


SYMBOL = "600519"
DAY = date(2026, 11, 23)
START = midnight(DAY)
END = START + 86400
BARS = (Candle(START, END, 100, 102, 99, 101, 200, 20100, "lots"),)
MINUTE_START = START + (9 * 60 + 30) * 60
MINUTE_END = MINUTE_START + 120
MINUTE_BARS = (
    Candle(MINUTE_START, MINUTE_START + 60, 100, 100, 100, 100, 75, 7500, "shares", 75),
    Candle(MINUTE_START + 60, MINUTE_END, 101, 101, 101, 101, 125, 12625, "shares", 125),
)

def stock_service(primary, fallback):
    stocks = StockInfoService((primary, fallback))
    adjustment = AdjustmentService(primary)
    klines = KlineService((primary, fallback), adjustment)
    minute = fake_provider("minute-test")
    minute.get_klines.return_value = MINUTE_BARS
    calendar = Mock(name="calendar")
    calendar.name = "calendar-test"
    calendar.version = "test"
    calendar.get_calendar.return_value = TradingCalendar(DAY, DAY, (DAY,))
    profile = VolumeProfileService(klines, stocks, adjustment, (minute,), calendar)
    return SimpleNamespace(stocks=stocks, klines=klines, profile=profile), minute


def fake_provider(name):
    provider = Mock(name=name)
    provider.name = name
    provider.version = "test"
    provider.minute_history_limit = 3000
    provider.get_stock_info.return_value = StockInfo(SYMBOL, "测试股票", "SSE", "SH")
    provider.get_klines.return_value = BARS
    provider.get_corporate_actions.return_value = ()
    return provider


class StockMarketTests(TestCase):
    def setUp(self):
        self.first = fake_provider("tdx")
        self.second = fake_provider("fallback")
        self.market, self.minute = stock_service(self.first, self.second)

    def test_priority_timeout_empty_and_cached_fallback(self):
        self.first.get_stock_info.side_effect = ProviderUnavailable("连接超时")
        self.first.get_klines.return_value = ()
        self.assertEqual(self.market.stocks.get_stock(SYMBOL).source, "fallback")
        self.assertEqual(self.market.klines.get_history(SYMBOL, "day", "none", None, None, 10).source, "fallback")
        self.market.klines.get_history(SYMBOL, "day", "none", None, None, 10)
        self.second.get_klines.assert_called_once()

    def test_unknown_prefix_and_confirmed_missing_symbol(self):
        with self.assertRaises(StockNotFound):
            self.market.stocks.get_stock("999999")
        self.first.get_stock_info.side_effect = StockNotFound("列表无此代码")
        self.second.get_stock_info.side_effect = StockNotFound("列表无此代码")
        with self.assertRaises(StockNotFound):
            self.market.stocks.get_stock("600000")

    def test_estimated_profile_uses_and_caches_only_native_minutes(self):
        result = self.market.profile.calculate(SYMBOL, MINUTE_START + 12, MINUTE_END - 20)
        self.assertTrue(result.quality["complete"])
        self.assertEqual(result.source, "minute-test")
        self.assertEqual(result.quality["actual_start"], MINUTE_START)
        self.assertEqual(result.quality["actual_end"], MINUTE_END)
        self.assertEqual(result.distribution.total_volume, 200)
        self.assertEqual(result.distribution.poc.price_cents, 10100)
        self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
        self.minute.get_klines.assert_called_once_with(SYMBOL, "1m", "none", None, None, 3000)

    def test_data_sources_are_never_combined_to_fill_missing_minutes(self):
        self.minute.get_klines.return_value = MINUTE_BARS[:1]
        other_minute = fake_provider("other")
        other_minute.get_klines.return_value = MINUTE_BARS[1:]
        self.market.profile.minute_sources = (self.minute, other_minute)
        with self.assertRaises(MinuteCoverageError) as caught:
            self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertEqual(caught.exception.quality["missing_minute_count"], 1)
        self.assertEqual(len(caught.exception.quality["source_errors"]), 2)

    def test_timeout_empty_and_missing_adjustment_factors_report_failure(self):
        self.minute.get_klines.side_effect = ProviderUnavailable("连接超时")
        with self.assertRaises(MinuteCoverageError) as caught:
            self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertIn("超时", caught.exception.quality["source_errors"][0]["message"])
        self.minute.get_klines.side_effect = None
        self.minute.get_klines.return_value = ()
        with self.assertRaises(MinuteCoverageError):
            self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
        self.minute.get_klines.return_value = MINUTE_BARS
        self.first.get_corporate_actions.side_effect = ProviderUnavailable("因子不足")
        with self.assertRaises(MinuteCoverageError) as caught:
            self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertEqual(caught.exception.quality["minute_count"], 2)
        self.assertFalse(caught.exception.quality["factor_complete"])
        self.assertFalse(caught.exception.quality["complete"])

    def test_cached_in_progress_minute_cannot_become_complete_by_wall_clock(self):
        with patch("app.services.volume_profile.datetime", wraps=datetime) as clock:
            clock.now.return_value = datetime.fromtimestamp(MINUTE_END - 20, CHINA)
            with self.assertRaises(MinuteCoverageError):
                self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
            clock.now.return_value = datetime.fromtimestamp(MINUTE_END + 1, CHINA)
            with self.assertRaises(MinuteCoverageError):
                self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
        self.minute.get_klines.assert_called_once()

    def test_factor_version_invalidates_chart_and_profile_cache(self):
        prior = self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
        prior_chart = self.market.klines.get_chart(SYMBOL, "1d", None, None, 10)
        action = CorporateAction(date(2026, 11, 24), Fraction(10), Fraction(0), Fraction(0), Fraction(0))
        self.first.get_corporate_actions.return_value = (action,)
        with patch("app.core.cache.monotonic", return_value=monotonic() + 301):
            current = self.market.profile.calculate(SYMBOL, MINUTE_START, MINUTE_END)
            current_chart = self.market.klines.get_chart(SYMBOL, "1d", None, None, 10)
        self.assertNotEqual(prior.adjustment_version, current.adjustment_version)
        self.assertEqual(prior_chart.adjustment_version, prior.adjustment_version)
        self.assertEqual(current_chart.adjustment_version, current.adjustment_version)
        self.assertEqual(current.distribution.total_volume, prior.distribution.total_volume)
        self.assertEqual(current.distribution.poc.price_cents, prior.distribution.poc.price_cents - 100)
        self.assertEqual(current_chart.history.bars[0].close, prior_chart.history.bars[0].close - 1)
