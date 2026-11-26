"""Verify normalized TDX stock records without requiring a public quote server."""

import unittest
from datetime import datetime
from unittest.mock import patch

from app.core.exceptions import ProviderUnavailable, UnsupportedMarketData
from app.core.market_time import CHINA
from app.data.tdx import TdxConnection, TdxKlineData, TdxStockData


class FakeQuotes:
    def __init__(self):
        self.symbol_requests = 0
        self.bars_requests = 0
        self.bars_error = False

    def connect(self, ip, port, time_out):
        pass

    def disconnect(self):
        pass

    def get_security_count(self, market):
        return 1

    def get_security_list(self, market, start):
        self.symbol_requests += 1
        return [{"code": "600519", "name": "贵州茅台\x00", "volunit": 100}]

    def get_security_bars(self, frequency, market, symbol, start, offset):
        self.bars_requests += 1
        if self.bars_error:
            raise ValueError("invalid packet")
        return [{
            "datetime": "2024-11-22 09:35" if frequency == 0 else "2024-11-22 15:00",
            "open": 10,
            "high": 11,
            "low": 9,
            "close": 10,
            "vol": 10,
            "amount": 10000,
        }]


class TdxStockDataTests(unittest.TestCase):
    def setUp(self):
        self.source = FakeQuotes()
        factory = patch("app.data.tdx.TdxHq_API", return_value=self.source)
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        connection = TdxConnection(servers=(("127.0.0.1", 7709),))
        self.info = TdxStockData(connection)
        self.klines = TdxKlineData(connection)

    def test_stock_names_come_from_security_list_and_bse_is_explicitly_unsupported(self):
        info = self.info.get_stock_info("600519")
        self.assertEqual((info.symbol, info.name, info.exchange), ("600519", "贵州茅台", "SSE"))
        self.assertEqual(self.info.get_stock_info("600519"), info)
        self.assertEqual(self.source.symbol_requests, 1)
        with self.assertRaises(UnsupportedMarketData):
            self.info.get_stock_info("920001")

    def test_security_directory_uses_the_actual_page_length_for_the_next_offset(self):
        first = [{"code": "110001", "name": "转债", "volunit": 10}]
        second = [{"code": "600519", "name": "贵州茅台", "volunit": 100}]
        with (
            patch.object(self.source, "get_security_count", return_value=2),
            patch.object(self.source, "get_security_list", side_effect=(first, second)) as read,
        ):
            self.assertEqual(self.info.get_stock_info("600519").name, "贵州茅台")
        self.assertEqual([item.args for item in read.call_args_list], [(1, 0), (1, 1)])

    def test_klines_use_reported_period_and_reconcile_lot_volume_with_amount(self):
        bars = self.klines.get_klines("600519", "5m", "none", None, None, 1)
        self.assertEqual(len(bars), 1)
        self.assertEqual(datetime.fromtimestamp(bars[0].timestamp, CHINA).strftime("%H:%M"), "09:30")
        self.assertEqual(bars[0].end_timestamp - bars[0].timestamp, 300)
        self.assertEqual((bars[0].volume, bars[0].original_volume_unit), (1000, "lots"))
        with self.assertRaises(UnsupportedMarketData):
            self.klines.get_klines("600519", "day", "qfq", None, None, 1)

    def test_one_minute_preserves_native_duplicates_for_quality_check(self):
        rows = self.source.get_security_bars(8, 1, "600519", 0, 2)
        with patch.object(self.source, "get_security_bars", return_value=rows * 2):
            bars = self.klines.get_klines("600519", "1m", "none", None, None, 30)
        self.assertEqual(len(bars), 2)
        self.assertEqual(bars[0], bars[1])

    def test_kline_failure_cools_down_only_that_capability(self):
        self.source.bars_error = True
        for _ in range(2):
            with self.assertRaises(ProviderUnavailable):
                self.klines.get_klines("600519", "day", "none", None, None, 1)
        self.assertEqual(self.source.bars_requests, 1)
        self.assertEqual(self.info.get_stock_info("600519").name, "贵州茅台")

    def test_conflicting_candles_with_the_same_timestamp_are_rejected(self):
        row = self.source.get_security_bars(0, 1, "600519", 0, 1)[0]
        with patch.object(self.source, "get_security_bars", return_value=[row, {**row, "close": 10.5}]):
            with self.assertRaisesRegex(ProviderUnavailable, "重复时间记录存在冲突"):
                self.klines.get_klines("600519", "5m", "none", None, None, 2)
