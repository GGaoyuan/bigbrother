from datetime import date, datetime
from time import monotonic
from unittest import TestCase
from unittest.mock import Mock, patch

from app.data.stock_adjustment import build_tdx_qfq
from app.data.stock_market import StockMarket
from app.data.stock_market_types import (
    CHINA, Candle, MinuteCoverageError, ProviderUnavailable, StockInfo, StockNotFound, Tick, TickCoverage,
    TickCoverageError, TickDay, midnight,
)


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
IDENTITY_FACTORS = build_tdx_qfq([{"year": 2026, "month": 1, "day": 1, "category": 5}], as_of=DAY)


def stock_service(primary, fallback):
    minute = fake_provider("akshare-sina")
    minute.get_klines.return_value = MINUTE_BARS
    return StockMarket((primary, fallback), minute_providers=(minute,), calendar_reader=lambda: (DAY,)), minute
ROWS = (
    Tick(START + 34200, 100, 50, 5000, "SELL", "1"),
    Tick(START + 34200, 100, 50, 5000, "SELL", "2"),
    Tick(START + 34300, 101, 100, 10100, "BUY", "3"),
)


def fake_provider(name, *, exact=True):
    provider = Mock(name=name)
    provider.name = name
    provider.version = "test"
    provider.get_stock_info.return_value = StockInfo(SYMBOL, "测试股票", "SSE", "SH")
    provider.get_klines.return_value = BARS
    provider.get_adjustment_factors.return_value = IDENTITY_FACTORS
    provider.get_ticks.return_value = TickDay(DAY, ROWS, True, "execution", "shares", exact)
    provider.get_tick_coverage.return_value = TickCoverage(None, None, None, True, True, False, "execution")
    return provider


class StockMarketTests(TestCase):
    def setUp(self):
        self.first = fake_provider("tdx")
        self.second = fake_provider("fallback")
        self.market, self.minute = stock_service(self.first, self.second)

    def test_priority_timeout_empty_and_cached_fallback(self):
        self.first.get_stock_info.side_effect = ProviderUnavailable("连接超时")
        self.first.get_klines.return_value = ()
        self.assertEqual(self.market.stock(SYMBOL)["source"], "fallback")
        self.assertEqual(self.market.klines(SYMBOL, "day", "none", None, None, 10)["source"], "fallback")
        self.market.klines(SYMBOL, "day", "none", None, None, 10)
        self.second.get_klines.assert_called_once()
        self.market.klines(SYMBOL, "day", "qfq", None, None, 10)
        self.assertEqual(self.second.get_klines.call_count, 2)

    def test_unknown_prefix_and_confirmed_missing_symbol(self):
        with self.assertRaises(StockNotFound):
            self.market.stock("999999")
        self.first.get_stock_info.side_effect = StockNotFound("列表无此代码")
        self.second.get_stock_info.side_effect = StockNotFound("列表无此代码")
        with self.assertRaises(StockNotFound):
            self.market.stock("600000")

    def test_cursor_stays_on_provider_and_identical_trades_remain(self):
        first = self.market.ticks(SYMBOL, START, END, 1, None)
        self.assertEqual(first["ticks"][0].trade_id, "1")
        self.assertFalse(first["complete"])
        self.assertTrue(first["day_complete"])
        second = self.market.ticks(SYMBOL, START, END, 10, first["next_cursor"])
        self.assertEqual([row.trade_id for row in second["ticks"]], ["2", "3"])
        self.assertTrue(second["complete"])
        self.assertIsNone(second["next_cursor"])
        with self.assertRaises(TickCoverageError):
            self.market.ticks(SYMBOL, START, END - 1, 10, first["next_cursor"])

    def test_estimated_profile_uses_and_caches_only_native_minutes(self):
        result = self.market.volume_profile(SYMBOL, MINUTE_START + 12, MINUTE_END - 20)
        self.assertTrue(result["complete"])
        self.assertEqual(result["source"], "akshare-sina")
        self.assertEqual(result["calculation_method"], "estimated_1m_weighted_range")
        self.assertEqual(result["actual_start"], MINUTE_START)
        self.assertEqual(result["actual_end"], MINUTE_END)
        self.assertEqual(result["profile"]["total"], 200)
        self.assertEqual(result["profile"]["poc"]["priceCents"], 10100)
        self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.minute.get_klines.assert_called_once_with(SYMBOL, "1m", "none", None, None, 3000)
        self.first.get_ticks.assert_not_called()

    def test_data_sources_are_never_combined_to_fill_missing_minutes(self):
        self.minute.get_klines.return_value = MINUTE_BARS[:1]
        other_minute = fake_provider("other")
        other_minute.get_klines.return_value = MINUTE_BARS[1:]
        self.market.minute_providers = (self.minute, other_minute)
        with self.assertRaises(MinuteCoverageError) as caught:
            self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertEqual(caught.exception.quality["missing_minute_count"], 1)
        self.assertEqual(len(caught.exception.quality["source_errors"]), 2)

    def test_timeout_empty_and_missing_adjustment_factors_report_failure(self):
        self.minute.get_klines.side_effect = ProviderUnavailable("连接超时")
        with self.assertRaises(MinuteCoverageError) as caught:
            self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertIn("超时", caught.exception.quality["source_errors"][0]["message"])
        self.minute.get_klines.side_effect = None
        self.minute.get_klines.return_value = ()
        with self.assertRaises(MinuteCoverageError):
            self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.minute.get_klines.return_value = MINUTE_BARS
        self.first.get_adjustment_factors.side_effect = ProviderUnavailable("因子不足")
        with self.assertRaises(MinuteCoverageError) as caught:
            self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertEqual(caught.exception.quality["minute_count"], 2)
        self.assertFalse(caught.exception.quality["factor_complete"])
        self.assertFalse(caught.exception.quality["complete"])

    def test_cached_in_progress_minute_cannot_become_complete_by_wall_clock(self):
        with patch("app.data.stock_market.datetime", wraps=datetime) as clock:
            clock.now.return_value = datetime.fromtimestamp(MINUTE_END - 20, CHINA)
            with self.assertRaises(MinuteCoverageError):
                self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
            clock.now.return_value = datetime.fromtimestamp(MINUTE_END + 1, CHINA)
            with self.assertRaises(MinuteCoverageError):
                self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.minute.get_klines.assert_called_once()

    def test_factor_version_invalidates_chart_and_profile_cache(self):
        prior = self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        prior_chart = self.market.chart_klines(SYMBOL, "1d", None, None, 10)
        action = {
            "year": 2026, "month": 11, "day": 24, "category": 1, "fenhong": 10,
            "songzhuangu": 0, "peigu": 0, "peigujia": 0,
        }
        newer = build_tdx_qfq([action], as_of=date(2026, 11, 24))
        self.first.get_adjustment_factors.return_value = newer
        with patch("app.data.stock_market.monotonic", return_value=monotonic() + 301):
            current = self.market.volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
            current_chart = self.market.chart_klines(SYMBOL, "1d", None, None, 10)
        self.assertNotEqual(prior["adjustment_version"], current["adjustment_version"])
        self.assertEqual(prior_chart["adjustment_version"], prior["adjustment_version"])
        self.assertEqual(current_chart["adjustment_version"], current["adjustment_version"])
        self.assertEqual(current["total_volume"], prior["total_volume"])
        self.assertEqual(current["poc"], prior["poc"] - 1)
        self.assertEqual(current_chart["bars"][0].close, prior_chart["bars"][0].close - 1)

    def test_second_source_is_never_spliced_into_existing_cursor(self):
        first = self.market.ticks(SYMBOL, START, END, 1, None)
        self.market = StockMarket((self.first, self.second))
        self.first.get_ticks.side_effect = ProviderUnavailable("首次来源失联")
        with self.assertRaises(TickCoverageError):
            self.market.ticks(SYMBOL, START, END, 10, first["next_cursor"])
        self.second.get_ticks.assert_not_called()

    def test_source_pagination_and_time_coverage_are_distinct(self):
        covered_until = START + 15 * 3600 + 60
        self.first.get_ticks.return_value = TickDay(
            DAY, ROWS, True, "aggregate", "lots", False,
            "盘后未核验", verified_until=covered_until,
        )
        data = self.market.ticks(SYMBOL, START, END, 10, None)
        self.assertTrue(data["pagination_complete"])
        self.assertFalse(data["complete"])
        self.assertFalse(data["day_complete"])
        self.assertEqual(data["verified_until"], covered_until)
        regular = self.market.ticks(SYMBOL, START, covered_until, 10, None)
        self.assertTrue(regular["complete"])
        self.assertTrue(regular["day_complete"])
