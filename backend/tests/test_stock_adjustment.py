import unittest
from datetime import date, datetime, time
from unittest.mock import Mock, patch

from dataclasses import replace
from fractions import Fraction

from app.core.exceptions import ProviderUnavailable, UnsupportedMarketData
from app.core.market_time import CHINA, candle_span, midnight
from app.models.corporate_action import CorporateAction
from app.models.kline import Candle
from app.data.tdx import TdxConnection, TdxCorporateActionData, normalize_actions
from app.services.adjustment import build_qfq


def action(day, *, cash=0, bonus=0, rights=0, rights_price=0):
    return CorporateAction(day, *(Fraction(str(value)) for value in (cash, bonus, rights, rights_price)))


def tdx_action(day, *, cash=0):
    return {
        "category": 1, "year": day.year, "month": day.month, "day": day.day,
        "fenhong": cash, "songzhuangu": 0, "peigu": 0, "peigujia": 0,
    }


def factors_for(actions, *, as_of):
    return build_qfq(tuple(actions), as_of=as_of, source="mootdx")


def candle(day, *, price=100, minute=False):
    label = datetime.combine(day, time(9, 30), CHINA) if minute else day
    stamp, end_stamp = candle_span(label, "1m" if minute else "day")
    return Candle(stamp, end_stamp, price, price + 1, price - 1, price, 1000, 100000, "shares")


class AdjustmentFactorsTests(unittest.TestCase):
    def test_composes_mixed_events_and_uses_same_basis_for_minute_and_daily(self):
        split = date(2023, 4, 26)
        dividend = date(2024, 4, 30)
        as_of = date(2024, 5, 1)
        # Ningde Times TDX events around its 2023 transfer of eight shares per ten.
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
        self.assertEqual(factors.source, "mootdx")
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
        # China Merchants Bank 2013 TDX rights event. Its subscription input
        # has binary floating-point noise, far below chart price precision.
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


class TdxAdjustmentSourceTests(unittest.TestCase):
    def test_requires_metadata_and_rejects_malformed_actions(self):
        day = date(2024, 7, 1)
        stock_change = {"category": 5, "year": 2024, "month": 7, "day": 1}
        self.assertEqual(normalize_actions([stock_change]), ())
        for rows in (None, [], [{"category": 5}], [tdx_action(day, cash=float("nan"))], [tdx_action(day, cash=-1)]):
            with self.subTest(rows=rows), self.assertRaises(ProviderUnavailable):
                normalize_actions(rows)

    def test_reads_symbol_specific_events_when_the_security_directory_is_unavailable(self):
        source = Mock()
        source.get_security_count.side_effect = TimeoutError("证券目录不可用")

        def events(market, symbol):
            if (market, symbol) == (0, "300604"):
                return [tdx_action(date(2026, 10, 30), cash=1)]
            return []

        source.get_xdxr_info.side_effect = events
        with patch("app.data.tdx.TdxHq_API", return_value=source):
            provider = TdxCorporateActionData(TdxConnection(servers=(("127.0.0.1", 7709),)))
            events = provider.get_corporate_actions("300604")
            self.assertEqual(events, (action(date(2026, 10, 30), cash=1),))
            with self.assertRaises(ProviderUnavailable):
                provider.get_corporate_actions("600001")
            with self.assertRaises(UnsupportedMarketData):
                provider.get_corporate_actions("920001")
        source.get_security_count.assert_not_called()
        source.get_security_list.assert_not_called()
        source.get_xdxr_info.assert_any_call(0, "300604")

    def test_unverified_empty_payload_retries_another_host(self):
        primary, secondary = Mock(), Mock()
        primary.get_xdxr_info.return_value = []
        secondary.get_xdxr_info.return_value = [tdx_action(date(2024, 6, 19), cash=308.76)]
        servers = (("127.0.0.1", 7709), ("127.0.0.2", 7709))
        with patch("app.data.tdx.TdxHq_API", side_effect=(primary, secondary)):
            provider = TdxCorporateActionData(TdxConnection(servers=servers))
            events = provider.get_corporate_actions("600519")
        self.assertEqual(events, (action(date(2024, 6, 19), cash=308.76),))
        secondary.get_xdxr_info.assert_called_once_with(1, "600519")

    def test_reconnects_an_existing_socket_after_the_server_closes_it(self):
        from tdxpy.exceptions import TdxFunctionCallError
        from tdxpy.parser.base import ResponseHeaderRecvFails

        closed = TdxFunctionCallError("calling function error")
        closed.original_exception = ResponseHeaderRecvFails("head_buf is not 0x10 : b''")
        cached, refreshed = Mock(), Mock()
        actions = [tdx_action(date(2026, 10, 30), cash=1)]
        cached.get_xdxr_info.side_effect = (actions, closed)
        refreshed.get_xdxr_info.return_value = actions
        with patch("app.data.tdx.TdxHq_API", side_effect=(cached, refreshed)):
            provider = TdxCorporateActionData(TdxConnection(servers=(("127.0.0.1", 7709),)))
            provider.get_corporate_actions("300604")
            events = provider.get_corporate_actions("300604")

        self.assertEqual(events, (action(date(2026, 10, 30), cash=1),))
        cached.disconnect.assert_called_once()
        refreshed.connect.assert_called_once_with("127.0.0.1", 7709, time_out=3)
        refreshed.get_xdxr_info.assert_called_once_with(0, "300604")

    def test_empty_actions_for_one_stock_do_not_disable_the_provider_for_another(self):
        source = Mock()
        source.get_xdxr_info.side_effect = ([], [tdx_action(date(2026, 10, 30), cash=1)])
        with patch("app.data.tdx.TdxHq_API", return_value=source):
            provider = TdxCorporateActionData(TdxConnection(servers=(("127.0.0.1", 7709),)))
            with self.assertRaises(ProviderUnavailable):
                provider.get_corporate_actions("300999")
            events = provider.get_corporate_actions("300604")
        self.assertEqual(events, (action(date(2026, 10, 30), cash=1),))
