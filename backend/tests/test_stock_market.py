from dataclasses import replace
from datetime import date, datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from app.api import kline, stock, volume_profile
from app.api.volume_profile import MinuteCoverageError
from app.core.exceptions import ProviderUnavailable, StockNotFound
from app.core.market_time import CHINA, midnight
from app.models.calendar.model import TradingCalendar
from app.models.kline.model import Candle
from app.models.stock.model import StockInfo


SYMBOL = "600519"
DAY = date(2026, 11, 23)
START = midnight(DAY)
END = START + 86400
BARS = (Candle(START, END, 100, 102, 99, 101, 200, 20100, "lots", adjustment="qfq"),)
MINUTE_START = START + (9 * 60 + 30) * 60
MINUTE_END = MINUTE_START + 120
MINUTE_BARS = (
    Candle(MINUTE_START, MINUTE_START + 60, 100, 100, 100, 100, 75, 7500, "shares", 75, adjustment="qfq"),
    Candle(MINUTE_START + 60, MINUTE_END, 101, 101, 101, 101, 125, 12625, "shares", 125, adjustment="qfq"),
)


def mock_market(test: TestCase, source):
    minute = Mock()
    minute.get_klines.return_value = MINUTE_BARS

    def get_bars(symbol, interval, *args):
        if interval == "1m":
            return minute.get_klines(symbol, interval, *args)
        return source.get_klines.return_value

    source.get_klines.side_effect = get_bars
    for patcher in (
        patch.object(stock, "provider", source),
        patch.object(kline, "provider", source),
        patch.object(volume_profile, "_calendar_provider", source.calendar),
    ):
        patcher.start()
        test.addCleanup(patcher.stop)
    return minute


def fake_provider(name):
    provider = Mock(name=name)
    provider.name = name
    provider.version = "test"
    provider.adjustment_version = "native-qfq:2026-11-23"
    provider.calendar.name = "calendar-test"
    provider.calendar.version = "test"
    provider.calendar.get_calendar.return_value = TradingCalendar(DAY, DAY, (DAY,))
    provider.get_stock_info.return_value = StockInfo(SYMBOL, "测试股票", "SSE", "SH")
    provider.get_klines.return_value = BARS
    return provider


class StockMarketTests(TestCase):
    def setUp(self):
        self.provider = fake_provider("easy-tdx-test")
        self.minute = mock_market(self, self.provider)

    def test_stock_info_fetches_fresh_data_each_time(self):
        self.assertEqual(stock.get_stock(SYMBOL).name, "测试股票")
        self.provider.get_stock_info.return_value = replace(self.provider.get_stock_info.return_value, name="更新名称")
        self.assertEqual(stock.get_stock(SYMBOL).name, "更新名称")
        self.assertEqual(self.provider.get_stock_info.call_count, 2)

    def test_history_fetches_fresh_data_each_time(self):
        source = kline.provider
        self.assertEqual(kline.get_history(SYMBOL, "1d", None, None, 10).source, source.name)
        source.get_klines.return_value = (replace(BARS[0], close=101.5),)
        self.assertEqual(kline.get_history(SYMBOL, "1d", None, None, 10).bars[0].close, 101.5)
        self.assertEqual(source.get_klines.call_count, 2)

    def test_unknown_prefix_and_confirmed_missing_symbol(self):
        with self.assertRaises(StockNotFound):
            stock.get_stock("999999")
        self.provider.get_stock_info.side_effect = StockNotFound("列表无此代码")
        with self.assertRaises(StockNotFound):
            stock.get_stock("600000")

    def test_chart_rejects_conflicting_rows_without_changing_source(self):
        kline.provider.get_klines.return_value = (*BARS, replace(BARS[0], close=101.5))
        with self.assertRaisesRegex(ProviderUnavailable, "冲突的重复时间"):
            kline.get_history(SYMBOL, "1d", None, None, 10)
        self.provider.get_klines.assert_called_once()

    def test_profile_rejects_invalid_calendar_before_requesting_prices(self):
        self.provider.calendar.get_calendar.return_value = TradingCalendar(DAY, DAY, (DAY, DAY))
        with self.assertRaisesRegex(ProviderUnavailable, "交易日历返回日期无效"):
            volume_profile.get_volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        kline.provider.get_klines.assert_not_called()

    def test_profile_fetches_and_calculates_again_for_identical_requests(self):
        with patch.object(volume_profile, "calculate_profile", wraps=volume_profile.calculate_profile) as calculate:
            result = volume_profile.get_volume_profile(SYMBOL, MINUTE_START + 12, MINUTE_END - 20)
            again = volume_profile.get_volume_profile(SYMBOL, MINUTE_START + 12, MINUTE_END - 20)
        self.assertEqual(again, result)
        self.assertTrue(result.quality["complete"])
        self.assertEqual(result.source, kline.provider.name)
        self.assertEqual(result.quality["actual_start"], MINUTE_START)
        self.assertEqual(result.quality["actual_end"], MINUTE_END)
        self.assertEqual(result.distribution.total_volume, 200)
        self.assertEqual(result.distribution.poc.price_cents, 10100)
        self.assertEqual(calculate.call_count, 2)
        self.assertEqual(self.minute.get_klines.call_count, 2)
        self.minute.get_klines.assert_called_with(SYMBOL, "1m", "qfq", START, END, 366 * 240)
        requests = [call.args[1:3] for call in kline.provider.get_klines.call_args_list]
        self.assertEqual(requests, [("1d", "qfq"), ("1m", "qfq")] * 2)
        self.assertEqual(self.provider.calendar.get_calendar.call_count, 2)
        self.assertEqual(self.provider.get_stock_info.call_count, 2)
        self.provider.get_corporate_actions.assert_not_called()

    def test_missing_minutes_are_reported_for_the_configured_source(self):
        self.minute.get_klines.return_value = MINUTE_BARS[:1]
        with self.assertRaises(MinuteCoverageError) as caught:
            volume_profile.get_volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertEqual(caught.exception.quality["missing_minute_count"], 1)
        error, = caught.exception.quality["source_errors"]
        self.assertEqual(error["source"], kline.provider.name)

    def test_timeout_empty_and_wrong_price_basis_report_failure(self):
        self.minute.get_klines.side_effect = ProviderUnavailable("连接超时")
        with self.assertRaises(MinuteCoverageError) as caught:
            volume_profile.get_volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertIn("超时", caught.exception.quality["source_errors"][0]["message"])
        self.minute.get_klines.side_effect = None
        self.minute.get_klines.return_value = ()
        with self.assertRaises(MinuteCoverageError):
            volume_profile.get_volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.minute.get_klines.return_value = tuple(replace(bar, adjustment="none") for bar in MINUTE_BARS)
        with self.assertRaises(MinuteCoverageError) as caught:
            volume_profile.get_volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        self.assertEqual(caught.exception.quality["invalid_count"], 2)
        self.assertFalse(caught.exception.quality["factor_complete"])
        self.assertFalse(caught.exception.quality["complete"])

    def test_intraday_profile_refetches_after_current_minute_closes(self):
        requested_end = END
        with patch("app.api.volume_profile.datetime", wraps=datetime) as clock:
            clock.now.return_value = datetime.fromtimestamp(MINUTE_END - 20, CHINA)
            result = volume_profile.get_volume_profile(SYMBOL, MINUTE_START, requested_end)
            self.assertEqual(result.quality["requested_end"], requested_end)
            self.assertEqual(result.quality["actual_end"], MINUTE_END - 60)
            self.assertEqual(result.quality["aligned_end"], MINUTE_END - 60)
            self.assertEqual(result.quality["invalid_count"], 0)
            self.assertEqual(result.quality["missing_minute_count"], 0)
            self.assertEqual(result.distribution.total_volume, MINUTE_BARS[0].volume)

            clock.now.return_value = datetime.fromtimestamp(MINUTE_END + 1, CHINA)
            refreshed = volume_profile.get_volume_profile(SYMBOL, MINUTE_START, requested_end)
            self.assertEqual(refreshed.quality["actual_end"], MINUTE_END)
            self.assertEqual(refreshed.distribution.total_volume, 200)
        self.assertEqual(self.minute.get_klines.call_count, 2)

    def test_intraday_profile_still_rejects_missing_closed_minutes(self):
        self.minute.get_klines.return_value = MINUTE_BARS[1:]
        with patch("app.api.volume_profile.datetime", wraps=datetime) as clock:
            clock.now.return_value = datetime.fromtimestamp(MINUTE_END + 1, CHINA)
            with self.assertRaises(MinuteCoverageError) as caught:
                volume_profile.get_volume_profile(SYMBOL, MINUTE_START, END)
        self.assertEqual(caught.exception.quality["missing_minute_count"], 1)

    def test_chart_and_profile_report_the_same_native_qfq_version(self):
        prior = volume_profile.get_volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        prior_chart = kline.get_history(SYMBOL, "1d", None, None, 10)
        self.provider.adjustment_version = "native-qfq:2026-11-24"
        self.provider.get_klines.return_value = (replace(BARS[0], open=99, high=101, low=98, close=100),)
        self.minute.get_klines.return_value = tuple(
            replace(bar, open=bar.open - 1, high=bar.high - 1, low=bar.low - 1, close=bar.close - 1)
            for bar in MINUTE_BARS
        )
        current = volume_profile.get_volume_profile(SYMBOL, MINUTE_START, MINUTE_END)
        current_chart = kline.get_history(SYMBOL, "1d", None, None, 10)
        self.assertNotEqual(prior.adjustment_version, current.adjustment_version)
        self.assertEqual(prior_chart.adjustment_version, prior.adjustment_version)
        self.assertEqual(current_chart.adjustment_version, current.adjustment_version)
        self.assertEqual(current.distribution.total_volume, prior.distribution.total_volume)
        self.assertEqual(current.distribution.poc.price_cents, prior.distribution.poc.price_cents - 100)
        self.assertEqual(current_chart.bars[0].close, prior_chart.bars[0].close - 1)
