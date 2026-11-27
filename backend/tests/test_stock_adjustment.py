import unittest
from datetime import date, datetime, time
from unittest.mock import MagicMock, patch

from dataclasses import replace
from fractions import Fraction

from easy_tdx import Market
from pandas import DataFrame

from app.core.exceptions import ProviderUnavailable, UnsupportedMarketData
from app.core.market_time import CHINA, candle_span, midnight
from app.models.model import Candle, CorporateAction
from app.models.provider import MarketDataProvider
from app.services.adjustment_service import build_qfq


def action(day, *, cash=0, bonus=0, rights=0, rights_price=0):
    return CorporateAction(day, *(Fraction(str(value)) for value in (cash, bonus, rights, rights_price)))


def tdx_action(day, *, cash=0.4, bonus=0.8, rights=0.1, rights_price=6):
    return {
        "category": 1, "date": day.isoformat(),
        "fenhong": cash, "songzhuangu": bonus, "peigu": rights, "peigujia": rights_price,
    }


def factors_for(actions, *, as_of):
    return build_qfq(tuple(actions), as_of=as_of, source="easy-tdx")


def candle(day, *, price=100, minute=False):
    label = datetime.combine(day, time(9, 30), CHINA) if minute else day
    stamp, end_stamp = candle_span(label, "1m" if minute else "day")
    return Candle(stamp, end_stamp, price, price + 1, price - 1, price, 1000, 100000, "shares")


class AdjustmentFactorsTests(unittest.TestCase):
    def test_composes_mixed_events_and_uses_same_basis_for_minute_and_daily(self):
        split = date(2023, 4, 26)
        dividend = date(2024, 4, 30)
        as_of = date(2024, 5, 1)
        # 使用宁德时代 2023 年每 10 股转增 8 股相关的通达信除权事件。
        factors = factors_for([
            action(dividend, cash=50.279998779296875),
            action(split, cash=25.200000762939453, bonus=8),
        ], as_of=as_of)

        prior = date(2023, 4, 25)
        daily = factors.apply(candle(prior, price=400))
        minute = factors.apply(candle(prior, price=400, minute=True))
        self.assertEqual((daily.open, daily.high, daily.low, daily.close), (215.79, 216.35, 215.24, 215.79))
        self.assertEqual(minute.close, daily.close)
        self.assertEqual((daily.volume, daily.amount, daily.original_volume_unit), (1000, 100000, "shares"))
        self.assertEqual(factors.apply(candle(split)).close, 94.97)
        self.assertEqual(factors.apply(candle(dividend)).close, 100)
        self.assertEqual(factors.source, "easy-tdx")
        self.assertRegex(factors.version, r"^tdx-affine-qfq-v1:[\da-f]{64}$")

    def test_same_day_actions_use_a_common_share_base_and_a_stable_version(self):
        day = date(2024, 7, 1)
        prior = candle(date(2024, 6, 28), price=30)
        cash = action(day, cash=4, bonus=2)
        rights = action(day, rights=2, rights_price=6)
        second_rights = action(day, rights=1, rights_price=10)
        future = action(date(2024, 8, 1), cash=20)
        factors = factors_for([rights, cash, second_rights, rights, future], as_of=day)

        self.assertEqual(factors.apply(prior).close, 21.2)
        self.assertEqual(factors.version, factors_for([second_rights, cash, rights], as_of=day).version)
        self.assertNotEqual(
            factors.version, factors_for([cash, rights, second_rights, future], as_of=date(2024, 8, 1)).version,
        )

    def test_rights_event_after_an_earlier_cash_dividend(self):
        # 使用招商银行 2013 年配股的通达信除权事件。配股数据的二进制浮点误差
        # 远小于图表价格精度。
        day = date(2013, 9, 5)
        factors = factors_for([
            action(day, rights=1.7400000095367432, rights_price=9.289999961853027),
            action(date(2013, 6, 28), cash=6.3),
        ], as_of=day)
        self.assertEqual(factors.apply(candle(date(2013, 9, 4), price=12)).close, 11.6)
        self.assertEqual(factors.apply(candle(date(2013, 6, 27), price=12)).close, 11.06)

    def test_chart_prices_round_half_up_on_the_final_result(self):
        factors = factors_for([action(date(2024, 7, 1), cash=0.25)], as_of=date(2024, 7, 1))
        self.assertEqual(factors.apply(candle(date(2024, 6, 28), price=10)).close, 9.98)

    def test_identity_keeps_prices_and_marks_the_result_forward_adjusted(self):
        day = date(2024, 7, 1)
        original = candle(day, price=10)
        self.assertEqual(factors_for([], as_of=day).apply(original), replace(original, adjustment="qfq"))

    def test_nonpositive_adjusted_prices_and_bars_spanning_an_action_fail(self):
        action_day = date(2024, 7, 1)
        factors = factors_for([action(action_day, cash=100)], as_of=action_day)
        with self.assertRaises(UnsupportedMarketData):
            factors.apply(candle(date(2024, 6, 28), price=10))

        bar = Candle(midnight(date(2024, 6, 28)), midnight(date(2024, 7, 2)), 20, 21, 19, 20, 100, None, "shares")
        with self.assertRaises(UnsupportedMarketData):
            factors.apply(bar)


class CorporateActionProviderTests(unittest.TestCase):
    @patch("app.models.provider.TdxClient")
    def test_converts_per_share_values_to_the_existing_per_ten_share_model(self, factory):
        day = date(2026, 11, 20)
        client = factory.return_value.__enter__.return_value
        client.get_xdxr_info.return_value = DataFrame([tdx_action(day)])
        provider = MarketDataProvider(tdx_servers=("one",))

        events = provider.get_corporate_actions("601888")

        self.assertEqual(events, (action(day, cash=4, bonus=8, rights=1, rights_price=6),))
        client.get_security_count.assert_not_called()
        client.get_xdxr_info.assert_called_once_with(Market.SH, "601888")

    @patch("app.models.provider.TdxClient")
    def test_empty_and_malformed_payloads_are_rejected(self, factory):
        provider = MarketDataProvider(tdx_servers=("one",))
        client = factory.return_value.__enter__.return_value
        day = date(2024, 7, 1)
        for rows in ([], [{"category": 5}], [tdx_action(day, cash=float("nan"))], [tdx_action(day, bonus=-1)]):
            client.get_xdxr_info.return_value = DataFrame(rows)
            with self.subTest(rows=rows), self.assertRaises(ProviderUnavailable):
                provider.get_corporate_actions("600519")

        client.get_xdxr_info.return_value = DataFrame([{"category": 5, "date": day.isoformat()}])
        self.assertEqual(provider.get_corporate_actions("600519"), ())

    @patch("app.models.provider.TdxClient")
    def test_unverified_empty_payload_uses_another_host_of_the_same_sdk(self, factory):
        primary, alternate = MagicMock(), MagicMock()
        primary.__enter__.return_value.get_xdxr_info.return_value = DataFrame()
        day = date(2026, 10, 30)
        alternate.__enter__.return_value.get_xdxr_info.return_value = DataFrame([
            tdx_action(day, cash=0.1, bonus=0, rights=0, rights_price=0),
        ])
        factory.side_effect = (primary, alternate)

        events = MarketDataProvider(tdx_servers=("one", "two")).get_corporate_actions("300604")

        self.assertEqual(events, (action(day, cash=1),))
        primary.__exit__.assert_called_once()
        alternate.__exit__.assert_called_once()
