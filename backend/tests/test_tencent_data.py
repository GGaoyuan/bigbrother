import unittest
from datetime import date, datetime, time, timedelta
from unittest.mock import patch

from pandas import DataFrame

from app.data.tencent import TencentStockData, TencentKlineData
from app.core.exceptions import ProviderUnavailable, StockNotFound, UnsupportedMarketData
from app.core.market_time import CHINA


class TencentDataTests(unittest.TestCase):
    def setUp(self):
        self.info = TencentStockData()
        self.klines = TencentKlineData()
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

    @patch("app.data.tencent.tencent._tencent_qt_snapshot")
    @patch("app.data.tencent.tencent.tencent_quote")
    def test_bare_000001_is_never_resolved_as_the_shanghai_index(self, quote, snapshot):
        quote.return_value = {"sz000001": {"name": "平安银行"}}
        info = self.info.get_stock_info("000001")
        self.assertEqual((info.name, info.exchange, info.market), ("平安银行", "SZSE", "主板"))
        quote.assert_called_once_with(["sz000001"])
        quote.return_value = {}
        snapshot.return_value = self.snapshot
        with self.assertRaises(ProviderUnavailable):
            self.info.get_stock_info("000001")
        snapshot.side_effect = ValueError("腾讯没有 sz000001 这个代码")
        with self.assertRaises(StockNotFound):
            self.info.get_stock_info("000001")

    @patch("app.data.tencent.tencent.tencent_kline")
    def test_uses_tencent_close_labels_and_board_specific_volume_units(self, request):
        request.return_value = self.bars(datetime=["2024-11-04 13:05"], volume=[18.01])
        candle, = self.klines.get_klines("000001", "5m", "none", self.stamp(13, 0), self.stamp(13, 5), 10)
        self.assertEqual((candle.timestamp, candle.end_timestamp), (self.stamp(13, 0), self.stamp(13, 5)))
        self.assertEqual((candle.volume, candle.original_volume_unit, candle.amount), (1801, "lots", None))
        request.assert_called_once_with("sz000001", period="m5", adjust="", count=320)

        request.return_value = self.bars(date=[self.day.isoformat()], volume=[201])
        candle, = self.klines.get_klines("688981", "day", "none", None, None, 2)
        self.assertEqual((candle.volume, candle.original_volume_unit), (201, "shares"))

    @patch("app.data.tencent.tencent.tencent_kline")
    def test_latest_tencent_whole_lots_are_marked_as_rounded(self, request):
        request.return_value = self.bars(datetime=["2024-11-04 13:05"], volume=[18])
        normal, = self.klines.get_klines("000001", "1m", "none", None, None, 10)
        star, = self.klines.get_klines("688981", "1m", "none", None, None, 10)
        self.assertEqual((normal.volume, normal.original_volume_unit, normal.original_volume), (1800, "rounded_lots", 18))
        self.assertEqual((star.volume, star.original_volume_unit), (18, "shares"))

    @patch("app.data.tencent.tencent.tencent_kline")
    def test_minute_ranges_beyond_the_rolling_window_are_reported(self, request):
        request.return_value = self.bars(datetime=["2024-11-04 13:05"], volume=[18.01])
        with self.assertRaises(UnsupportedMarketData):
            self.klines.get_klines("000001", "5m", "none", self.stamp(12, 59), self.stamp(13, 5), 10)
        with self.assertRaises(UnsupportedMarketData):
            self.klines.get_klines("000001", "5m", "none", None, self.stamp(13, 0), 10)

    @patch("app.data.tencent.tencent.tencent_kline")
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
            self.klines.get_klines("000001", "week", "none", None, None, 10)
