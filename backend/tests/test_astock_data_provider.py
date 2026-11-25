import unittest
from datetime import date, datetime, time, timedelta
from unittest.mock import patch

from pandas import DataFrame

from app.data.astock_data_provider import AStockDataProvider
from app.data.stock_market_types import CHINA, ProviderUnavailable, StockNotFound, UnsupportedMarketData


class AStockDataProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = AStockDataProvider()
        self.day = date(2024, 11, 4)
        self.snapshot = (self.day.isoformat(), "160000", 10000000.0, 0.0)

    def stamp(self, hour, minute):
        return int(datetime.combine(self.day, time(hour, minute), CHINA).timestamp())

    @staticmethod
    def bars(**columns):
        return DataFrame({
            "open": [10],
            "high": [11],
            "low": [9],
            "close": [10.5],
            **columns,
        })

    @patch("app.data.astock_data_provider.tencent._tencent_qt_snapshot")
    @patch("app.data.astock_data_provider.tencent.tencent_quote")
    def test_bare_000001_is_never_resolved_as_the_shanghai_index(self, quote, snapshot):
        quote.return_value = {"sz000001": {"name": "平安银行"}}
        info = self.provider.get_stock_info("000001")
        self.assertEqual((info.name, info.exchange, info.market), ("平安银行", "SZSE", "主板"))
        quote.assert_called_once_with(["sz000001"])
        quote.return_value = {}
        snapshot.return_value = self.snapshot
        with self.assertRaises(ProviderUnavailable):
            self.provider.get_stock_info("000001")
        snapshot.side_effect = ValueError("腾讯没有 sz000001 这个代码")
        with self.assertRaises(StockNotFound):
            self.provider.get_stock_info("000001")

    @patch("app.data.astock_data_provider.tencent.tencent_kline")
    def test_uses_tencent_close_labels_and_board_specific_volume_units(self, request):
        request.return_value = self.bars(datetime=["2024-11-04 13:05"], volume=[18.01])
        candle, = self.provider.get_klines("000001", "5m", "none", self.stamp(13, 0), self.stamp(13, 5), 10)
        self.assertEqual((candle.timestamp, candle.end_timestamp), (self.stamp(13, 0), self.stamp(13, 5)))
        self.assertEqual((candle.volume, candle.original_volume_unit, candle.amount), (1801, "lots", None))
        request.assert_called_once_with("sz000001", period="m5", adjust="", count=320)

        request.return_value = self.bars(date=[self.day.isoformat()], volume=[201])
        candle, = self.provider.get_klines("688981", "day", "none", None, None, 2)
        self.assertEqual((candle.volume, candle.original_volume_unit), (201, "shares"))

    @patch("app.data.astock_data_provider.tencent.tencent_kline")
    def test_latest_tencent_whole_lots_are_marked_as_rounded(self, request):
        request.return_value = self.bars(datetime=["2024-11-04 13:05"], volume=[18])
        normal, = self.provider.get_klines("000001", "1m", "none", None, None, 10)
        star, = self.provider.get_klines("688981", "1m", "none", None, None, 10)
        self.assertEqual((normal.volume, normal.original_volume_unit, normal.original_volume), (1800, "rounded_lots", 18))
        self.assertEqual((star.volume, star.original_volume_unit), (18, "shares"))

    @patch("app.data.astock_data_provider.tencent.tencent_kline")
    def test_minute_ranges_beyond_the_rolling_window_are_reported(self, request):
        request.return_value = self.bars(datetime=["2024-11-04 13:05"], volume=[18.01])
        with self.assertRaises(UnsupportedMarketData):
            self.provider.get_klines("000001", "5m", "none", self.stamp(12, 59), self.stamp(13, 5), 10)
        with self.assertRaises(UnsupportedMarketData):
            self.provider.get_klines("000001", "5m", "none", None, self.stamp(13, 0), 10)

    @patch("app.data.astock_data_provider.tencent.tencent_kline")
    def test_conflicting_normalized_candles_do_not_silently_overwrite(self, request):
        request.return_value = DataFrame({
            "date": ["2024-11-04", "2024-11-08"],
            "open": [10, 10],
            "high": [11, 11],
            "low": [9, 9],
            "close": [10.1, 10.2],
            "volume": [18, 21],
        })
        with self.assertRaisesRegex(ProviderUnavailable, "冲突"):
            self.provider.get_klines("000001", "week", "none", None, None, 10)

    @patch("app.data.astock_data_provider.tencent._tencent_qt_snapshot")
    @patch("app.data.astock_data_provider.tencent.tencent_ticks")
    def test_provisional_or_complete_tencent_rows_stay_price_volume_inexact(self, ticks, snapshot):
        snapshot.return_value = self.snapshot
        frame = DataFrame({
            "date": [self.day.isoformat()] * 4,
            "code": ["sh688981"] * 4,
            "time": ["09:30:00", "09:30:03", "09:30:06", "09:30:09"],
            "seq": [0, 1, 2, 3],
            "price": [10.0, 10.1, 10.2, 10.2],
            "volume": [3, 5, 0, 1],
            "amount": [3001.0, 5042.0, 97.0, 1020.0],
            "side": ["B", "S", "M", "M"],
        })
        frame.attrs["complete"] = True
        frame.attrs["missing_seq"] = []
        ticks.return_value = frame

        result = self.provider.get_ticks("688981", self.day)
        self.assertTrue(result.complete)
        self.assertFalse(result.price_volume_exact)
        self.assertEqual(result.resolution, "aggregated_3s")
        self.assertEqual(result.original_volume_unit, "rounded_lots")
        self.assertEqual([row.side for row in result.ticks], ["BUY", "SELL", "UNKNOWN"])
        self.assertEqual([row.volume for row in result.ticks], [300, 500, 100])
        self.assertEqual(result.omitted_zero_lot_rows, 1)
        self.assertIn("省略了 1 条", result.reason)
        self.assertEqual(result.ticks[0].amount, 3001)
        self.assertIsNone(result.ticks[0].trade_id)
        self.assertIn("科创板", result.reason)

        frame.attrs["complete"] = None
        self.assertFalse(self.provider.get_ticks("688981", self.day).complete)

    @patch("app.data.astock_data_provider.tencent._tencent_qt_snapshot")
    @patch("app.data.astock_data_provider.tencent.tencent_ticks")
    def test_history_is_rejected_before_expensive_download_and_bad_paging_is_not_repaired(self, ticks, snapshot):
        snapshot.return_value = self.snapshot
        with self.assertRaises(UnsupportedMarketData):
            self.provider.get_ticks("600519", self.day - timedelta(days=3))
        ticks.assert_not_called()

        coverage = self.provider.get_tick_coverage("600519")
        self.assertEqual((coverage.start, coverage.end), (self.day, self.day))
        self.assertFalse(coverage.history_supported)
        self.assertIsNone(coverage.complete)
        ticks.assert_not_called()

        ticks.side_effect = RuntimeError("序号或时间倒退")
        with self.assertRaises(ProviderUnavailable):
            self.provider.get_ticks("600519", self.day)
