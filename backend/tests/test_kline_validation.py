from dataclasses import replace
from unittest import TestCase

from app.models.model import Candle
from app.services.kline_service import has_valid_ohlcv


class CandleModelTests(TestCase):
    def test_ohlcv_requires_valid_prices_shares_and_optional_turnover(self):
        bar = Candle(60, 120, 10.0, 11.0, 9.0, 10.5, 200, None, "shares")
        self.assertTrue(has_valid_ohlcv(bar))
        self.assertTrue(has_valid_ohlcv(replace(bar, volume=0, amount=0)))
        for fields in (
            {"high": 10.0}, {"low": 0.0}, {"close": float("nan")},
            {"volume": -1}, {"volume": 200.0}, {"volume": True},
            {"amount": -1.0}, {"amount": float("inf")},
        ):
            with self.subTest(fields=fields):
                self.assertFalse(has_valid_ohlcv(replace(bar, **fields)))
