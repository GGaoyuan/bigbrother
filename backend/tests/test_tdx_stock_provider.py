"""Verify normalized TDX stock records without requiring a public quote server."""

import unittest
from datetime import date, datetime
from unittest.mock import patch

from app.data.stock_market_types import CHINA, ProviderUnavailable, UnsupportedMarketData
from app.data.tdx_stock_provider import TdxProvider


DAY = date(2024, 11, 22)


class FakeQuotes:
    def __init__(self):
        self.symbol_requests = 0
        self.bars_requests = 0
        self.bars_error = False
        self.trades = [
            {"time": "09:25", "price": 10.02, "vol": 5, "buyorsell": 2},
            {"time": "09:30", "price": 10.01, "vol": 2, "buyorsell": 0},
            {"time": "09:30", "price": 10.01, "vol": 2, "buyorsell": 0},
            {"time": "15:00", "price": 10.08, "vol": 7, "buyorsell": 1},
            {"time": "15:20", "price": 10.08, "vol": 3, "buyorsell": 5},
        ]
        self.minute_volume = 16

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

    def get_history_transaction_data(self, market, symbol, start, offset, date):
        end = max(0, len(self.trades) - start)
        return self.trades[max(0, end - offset):end]

    def get_history_minute_time_data(self, market, code, date):
        return [{"vol": 0, "price": 10.0}] * 239 + [{"vol": self.minute_volume, "price": 10.08}]


class TdxStockProviderTests(unittest.TestCase):
    def setUp(self):
        self.source = FakeQuotes()
        factory = patch("app.data.tdx_stock_provider.TdxHq_API", return_value=self.source)
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        self.provider = TdxProvider(servers=(("127.0.0.1", 7709),))

    def test_stock_names_come_from_security_list_and_bse_is_explicitly_unsupported(self):
        info = self.provider.get_stock_info("600519")
        self.assertEqual((info.symbol, info.name, info.exchange), ("600519", "贵州茅台", "SSE"))
        self.assertEqual(self.provider.get_stock_info("600519"), info)
        self.assertEqual(self.source.symbol_requests, 1)
        with self.assertRaises(UnsupportedMarketData):
            self.provider.get_stock_info("920001")

    def test_security_directory_uses_the_actual_page_length_for_the_next_offset(self):
        first = [{"code": "110001", "name": "转债", "volunit": 10}]
        second = [{"code": "600519", "name": "贵州茅台", "volunit": 100}]
        with (
            patch.object(self.source, "get_security_count", return_value=2),
            patch.object(self.source, "get_security_list", side_effect=(first, second)) as read,
        ):
            self.assertEqual(self.provider.get_stock_info("600519").name, "贵州茅台")
        self.assertEqual([item.args for item in read.call_args_list], [(1, 0), (1, 1)])

    def test_klines_use_reported_period_and_reconcile_lot_volume_with_amount(self):
        bars = self.provider.get_klines("600519", "5m", "none", None, None, 1)
        self.assertEqual(len(bars), 1)
        self.assertEqual(datetime.fromtimestamp(bars[0].timestamp, CHINA).strftime("%H:%M"), "09:30")
        self.assertEqual(bars[0].end_timestamp - bars[0].timestamp, 300)
        self.assertEqual((bars[0].volume, bars[0].original_volume_unit), (1000, "lots"))
        with self.assertRaises(UnsupportedMarketData):
            self.provider.get_klines("600519", "day", "qfq", None, None, 1)

    def test_one_minute_preserves_native_duplicates_for_quality_check(self):
        rows = self.source.get_security_bars(8, 1, "600519", 0, 2)
        with patch.object(self.source, "get_security_bars", return_value=rows * 2):
            bars = self.provider.get_klines("600519", "1m", "none", None, None, 30)
        self.assertEqual(len(bars), 2)
        self.assertEqual(bars[0], bars[1])

    def test_historical_pages_preserve_identical_records_and_unknown_direction(self):
        with patch("app.data.tdx_stock_provider.TICK_PAGE_SIZE", 2):
            result = self.provider.get_ticks("600519", DAY)

        self.assertTrue(result.complete)
        self.assertFalse(result.price_volume_exact)
        self.assertEqual(result.resolution, "aggregated_minute_label")
        self.assertEqual([tick.side for tick in result.ticks], ["UNKNOWN", "BUY", "BUY", "SELL", "UNKNOWN"])
        self.assertEqual(result.ticks[1], result.ticks[2])
        self.assertEqual(sum(tick.volume for tick in result.ticks), 1900)
        self.assertTrue(all(tick.amount is None and tick.trade_id is None for tick in result.ticks))

    def test_volume_mismatch_does_not_claim_complete_ticks(self):
        self.source.minute_volume = 15
        result = self.provider.get_ticks("600519", DAY)
        self.assertFalse(result.complete)
        self.assertIn("成交量", result.reason or "")
        self.assertIsNone(self.provider.get_tick_coverage("600519").start)

    def test_zero_lot_groups_are_reported_but_never_exposed_as_positive_share_trades(self):
        self.source.trades.insert(2, {"time": "09:30", "price": 10.01, "vol": 0, "buyorsell": 0})
        self.source.trades.insert(5, {"time": "15:10", "price": 10.08, "vol": 0, "buyorsell": 5})
        result = self.provider.get_ticks("688981", DAY)

        self.assertTrue(result.complete)
        self.assertEqual(result.original_volume_unit, "rounded_lots")
        self.assertEqual(len(result.ticks), 5)
        self.assertEqual(result.omitted_zero_lot_rows, 2)
        self.assertTrue(all(tick.volume > 0 for tick in result.ticks))
        self.assertIn("省略 2 条零手聚合记录", result.reason or "")

    def test_kline_failure_cools_down_only_that_capability(self):
        self.source.bars_error = True
        for _ in range(2):
            with self.assertRaises(ProviderUnavailable):
                self.provider.get_klines("600519", "day", "none", None, None, 1)
        self.assertEqual(self.source.bars_requests, 1)
        self.assertTrue(self.provider.get_ticks("600519", DAY).complete)

    def test_conflicting_candles_with_the_same_timestamp_are_rejected(self):
        row = self.source.get_security_bars(0, 1, "600519", 0, 1)[0]
        with patch.object(self.source, "get_security_bars", return_value=[row, {**row, "close": 10.5}]):
            with self.assertRaisesRegex(ProviderUnavailable, "重复时间记录存在冲突"):
                self.provider.get_klines("600519", "5m", "none", None, None, 2)
