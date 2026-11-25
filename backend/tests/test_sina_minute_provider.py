"""Test normalization of native Sina one-minute candles via AKShare."""

import unittest
from datetime import datetime
from unittest.mock import patch

from pandas import DataFrame

from app.data.sina_minute_provider import SinaMinuteProvider
from app.data.stock_market_types import CHINA, ProviderUnavailable, UnsupportedMarketData


def unix_minute(label):
    return int(datetime.fromisoformat(label).replace(tzinfo=CHINA).timestamp())


def native_row(label, volume="62289", amount="90960209.5388"):
    return {
        "day": label,
        "open": "1457.550",
        "high": "1462.200",
        "low": "1457.240",
        "close": "1457.240",
        "volume": volume,
        "amount": amount,
    }


class SinaMinuteProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = SinaMinuteProvider()

    def test_native_ohlc_shares_and_yuan_are_preserved_at_right_labeled_minute(self):
        row = native_row("2026-11-24 14:57:00")
        with patch("app.data.sina_minute_provider.stock_zh_a_minute", return_value=DataFrame([row])) as fetch:
            bars = self.provider.get_klines("600519", "1m", "none", None, None, 3000)

        fetch.assert_called_once_with(symbol="sh600519", period="1", adjust="")
        self.assertEqual(len(bars), 1)
        bar = bars[0]
        self.assertEqual(bar.timestamp, unix_minute("2026-11-24 14:56:00"))
        self.assertEqual(bar.end_timestamp, unix_minute("2026-11-24 14:57:00"))
        self.assertEqual((bar.open, bar.high, bar.low, bar.close), (1457.55, 1462.2, 1457.24, 1457.24))
        self.assertEqual((bar.volume, bar.original_volume, bar.original_volume_unit), (62289, 62289, "shares"))
        self.assertEqual(bar.amount, 90960209.5388)

    def test_range_filters_half_open_overlap_and_does_not_collapse_duplicates(self):
        rows = [
            native_row("2026-11-24 15:00:00", "156000", "227760000"),
            native_row("2026-11-24 14:57:00"),
            native_row("2026-11-24 14:56:00"),
            native_row("2026-11-24 14:57:00", "1", "1457.24"),
        ]
        with patch("app.data.sina_minute_provider.stock_zh_a_minute", return_value=DataFrame(rows)) as fetch:
            bars = self.provider.get_klines(
                "000001", "1m", "none", unix_minute("2026-11-24 14:56:00"),
                unix_minute("2026-11-24 14:57:00"), 8,
            )

        fetch.assert_called_once_with(symbol="sz000001", period="1", adjust="")
        self.assertEqual([bar.volume for bar in bars], [62289, 1])
        self.assertEqual(bars[0].timestamp, bars[1].timestamp)

    def test_malformed_volume_and_source_failure_raise_provider_error(self):
        malformed = DataFrame([native_row("2026-11-24 14:57:00", "7.3")])
        with patch("app.data.sina_minute_provider.stock_zh_a_minute", return_value=malformed):
            with self.assertRaisesRegex(ProviderUnavailable, "成交量"):
                self.provider.get_klines("600519", "1m", "none", None, None, 3000)
        with patch("app.data.sina_minute_provider.stock_zh_a_minute", side_effect=TimeoutError):
            with self.assertRaises(ProviderUnavailable):
                self.provider.get_klines("600519", "1m", "none", None, None, 3000)

    def test_older_range_is_not_substituted_with_recent_rows(self):
        rows = DataFrame([native_row("2026-11-24 14:57:00")])
        with patch("app.data.sina_minute_provider.stock_zh_a_minute", return_value=rows):
            bars = self.provider.get_klines(
                "600519", "1m", "none", unix_minute("2026-09-22 09:30:00"),
                unix_minute("2026-09-22 15:00:00"), 3000,
            )
        self.assertEqual(bars, ())

    def test_only_unadjusted_hushen_one_minute_is_supported(self):
        for symbol, interval, adjust in (
            ("600519", "5m", "none"), ("600519", "1m", "qfq"), ("920001", "1m", "none"),
        ):
            with self.subTest(symbol=symbol, interval=interval, adjust=adjust):
                with self.assertRaises(UnsupportedMarketData):
                    self.provider.get_klines(symbol, interval, adjust, None, None, 3000)
