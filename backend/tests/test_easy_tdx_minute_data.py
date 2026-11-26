from datetime import date, datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from easy_tdx import Period
from easy_tdx.mac.enums import Adjust
from pandas import DataFrame

from app.data.easy_tdx_minutes import EasyTdxMinuteData
from app.core.exceptions import ProviderUnavailable
from app.core.market_time import CHINA, midnight


def stamp(hour, minute):
    return int(datetime(2026, 10, 14, hour, minute, tzinfo=CHINA).timestamp())


def frame(*labels, volume=600):
    return DataFrame([
        {"datetime": label, "open": 1298.969970703125, "high": 1300.18, "low": 1298.5,
         "close": 1300, "vol": volume, "amount": 10000}
        for label in labels
    ])


class EasyTdxMinuteTests(TestCase):
    def setUp(self):
        self.patch = patch("app.data.easy_tdx_minutes.MacClient")
        self.constructor = self.patch.start()
        self.addCleanup(self.patch.stop)
        self.client = self.constructor.return_value.__enter__.return_value
        self.provider = EasyTdxMinuteData(servers=("one", "two"))

    def test_pages_backwards_and_returns_right_labeled_bars_in_source_shares(self):
        self.client.get_stock_kline.side_effect = (
            frame("2026-10-14 09:33", "2026-10-14 09:34"),
            frame("2026-10-14 09:31", "2026-10-14 09:32"),
        )
        with patch("app.data.easy_tdx_minutes.PAGE_SIZE", 2):
            bars = self.provider.get_klines("600519", "1m", "none", stamp(9, 30), stamp(9, 33), 99)
        self.assertEqual([bar.timestamp for bar in bars], [stamp(9, 30), stamp(9, 31), stamp(9, 32)])
        self.assertEqual((bars[0].open, bars[0].volume, bars[0].original_volume), (1298.97, 600, 600))
        self.assertEqual((bars[0].original_volume_unit, bars[0].volume_precision_shares), ("shares", 100))
        self.assertEqual(
            [(call.args, call.kwargs) for call in self.client.get_stock_kline.call_args_list],
            [
                ((1, "600519", Period.MIN_1), {"start": 0, "count": 2, "adjust": Adjust.NONE}),
                ((1, "600519", Period.MIN_1), {"start": 2, "count": 2, "adjust": Adjust.NONE}),
            ],
        )

    def test_first_host_empty_then_uses_shenzhen_market_of_second_host(self):
        alternate = Mock()
        alternate.get_stock_kline.return_value = frame("2026-10-14 09:31")
        self.client.get_stock_kline.return_value = DataFrame()
        first, second = self.constructor.return_value, Mock()
        second.__enter__ = Mock(return_value=alternate)
        second.__exit__ = Mock(return_value=False)
        self.constructor.side_effect = (first, second)
        bars = self.provider.get_klines("000001", "1m", "none", None, None, 1)
        self.assertEqual(len(bars), 1)
        self.assertEqual(alternate.get_stock_kline.call_args.args[:2], (0, "000001"))

    def test_repeated_page_and_inconsistent_native_volume_are_rejected(self):
        first = EasyTdxMinuteData(servers=("one",))
        self.client.get_stock_kline.return_value = frame("2026-10-14 09:31", "2026-10-14 09:32")
        with patch("app.data.easy_tdx_minutes.PAGE_SIZE", 2):
            with self.assertRaisesRegex(ProviderUnavailable, "分页"):
                first.get_klines("688981", "1m", "none", midnight(date(2026, 10, 13)), stamp(10, 0), 99)
        self.client.get_stock_kline.return_value = frame("2026-10-14 09:31", volume=2.5)
        with self.assertRaisesRegex(ProviderUnavailable, "成交量"):
            first.get_klines("600519", "1m", "none", None, None, 5)
