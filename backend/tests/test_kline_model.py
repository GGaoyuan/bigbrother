from dataclasses import replace
from unittest import TestCase

from app.models.kline import Candle


class CandleModelTests(TestCase):
    def test_ohlcv_requires_valid_prices_shares_and_optional_turnover(self):
        bar = Candle(60, 120, 10.0, 11.0, 9.0, 10.5, 200, None, "shares")
        self.assertTrue(bar.has_valid_ohlcv())
        self.assertTrue(replace(bar, volume=0, amount=0).has_valid_ohlcv())
        for fields in (
            {"high": 10.0}, {"low": 0.0}, {"close": float("nan")},
            {"volume": -1}, {"volume": 200.0}, {"volume": True},
            {"amount": -1.0}, {"amount": float("inf")},
        ):
            with self.subTest(fields=fields):
                self.assertFalse(replace(bar, **fields).has_valid_ohlcv())
