"""验证单一行情 Provider 的股票资料查询。"""

from unittest import TestCase
from unittest.mock import patch

from easy_tdx import Market
from pandas import DataFrame

from app.core.exceptions import ProviderUnavailable, StockNotFound
from app.models.model import StockInfo
from app.models.provider import MarketDataProvider


class StockProviderTests(TestCase):
    def setUp(self):
        patcher = patch("app.models.provider.MacClient")
        self.factory = patcher.start()
        self.addCleanup(patcher.stop)
        self.client = self.factory.return_value.__enter__.return_value
        self.provider = MarketDataProvider(mac_servers=("one",))

    def test_reads_stock_info_from_its_quote(self):
        self.client.get_stock_quotes.return_value = DataFrame([
            {"market": int(Market.SH), "code": "600519", "name": "贵州茅台"},
        ])
        self.assertEqual(
            self.provider.get_stock_info("600519"),
            StockInfo("600519", "贵州茅台", "SSE", "主板"),
        )
        self.client.get_stock_quotes.assert_called_once_with([(int(Market.SH), "600519")])
        self.factory.return_value.__exit__.assert_called_once()

    def test_missing_symbol_is_distinct_from_wrong_quote_or_timeout(self):
        self.client.get_stock_quotes.return_value = DataFrame()
        with self.assertRaises(StockNotFound):
            self.provider.get_stock_info("000001")
        self.client.get_stock_quotes.return_value = DataFrame([
            {"market": int(Market.SZ), "code": "000002", "name": "万科 A"},
        ])
        with self.assertRaises(ProviderUnavailable):
            self.provider.get_stock_info("000001")
        self.client.get_stock_quotes.side_effect = TimeoutError("timed out")
        with self.assertRaisesRegex(ProviderUnavailable, "timed out"):
            self.provider.get_stock_info("000001")
