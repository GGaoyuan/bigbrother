from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from pandas import DataFrame

from app.core.market_time import CHINA
from app.data.easy_tdx_minutes import EasyTdxMinuteData
from app.data.tdx import TdxConnection, TdxKlineData, TdxStockData
from app.data.tencent import TencentKlineData, TencentStockData
from app.models.contracts import KlineDataSource, StockDataSource
from app.models.kline import Candle
from app.models.stock import StockInfo


class KlineDataContractTests(TestCase):
    def test_adapters_share_the_same_candle_semantics(self):
        raw_rows = [
            {
                "datetime": f"2024-11-04 09:{minute}",
                "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5,
                "vol": 1800, "amount": 18000.0,
            }
            for minute in (33, 32, 31)
        ]
        tdx_client = Mock()
        tdx_client.get_security_bars.return_value = raw_rows
        with (
            patch("app.data.tdx.TdxHq_API", return_value=tdx_client),
            patch("app.data.easy_tdx_minutes.MacClient") as mac_client,
            patch("app.data.tencent.tencent.tencent_kline") as tencent_kline,
        ):
            mac_client.return_value.__enter__.return_value.get_stock_kline.return_value = DataFrame(raw_rows)
            tencent_kline.return_value = DataFrame(raw_rows).rename(columns={"vol": "volume"})
            cases: tuple[tuple[KlineDataSource, float | None, int], ...] = (
                (TdxKlineData(TdxConnection(servers=(("127.0.0.1", 7709),))), 18000.0, 1),
                (EasyTdxMinuteData(servers=("test",)), None, 100),
                (TencentKlineData(), None, 1),
            )
            for source, amount, precision in cases:
                with self.subTest(source=source.name):
                    self.assert_minute_contract(source, amount, precision)

    def assert_minute_contract(
        self, source: KlineDataSource, amount: float | None, precision: int,
    ) -> None:
        start = int(datetime(2024, 11, 4, 9, 30, tzinfo=CHINA).timestamp())
        end = start + 120
        bars = source.get_klines("688981", "1m", "none", start, end, 10)

        self.assertIsInstance(bars, tuple)
        self.assertEqual([(bar.timestamp, bar.end_timestamp) for bar in bars], [
            (start, start + 60),
            (start + 60, end),
        ])
        for bar in bars:
            self.assertIsInstance(bar, Candle)
            self.assertTrue(bar.has_valid_ohlcv())
            self.assertEqual((bar.open, bar.high, bar.low, bar.close), (10.0, 11.0, 9.0, 10.5))
            self.assertEqual((bar.adjustment, bar.volume, bar.amount), ("none", 1800, amount))
            self.assertEqual((bar.original_volume_unit, bar.volume_precision_shares), ("shares", precision))


class StockDataContractTests(TestCase):
    def test_adapters_return_the_same_standard_stock_metadata(self):
        client = Mock()
        client.get_security_count.return_value = 1
        client.get_security_list.return_value = [{"code": "600519", "name": "贵州茅台\x00"}]
        with (
            patch("app.data.tdx.TdxHq_API", return_value=client),
            patch("app.data.tencent.tencent.tencent_quote", return_value={"sh600519": {"name": "贵州茅台"}}),
        ):
            sources: tuple[StockDataSource, ...] = (
                TdxStockData(TdxConnection(servers=(("127.0.0.1", 7709),))),
                TencentStockData(),
            )
            for source in sources:
                with self.subTest(source=source.name):
                    self.assertEqual(
                        source.get_stock_info("600519"),
                        StockInfo("600519", "贵州茅台", "SSE", "主板", "CNY", 0.01),
                    )
