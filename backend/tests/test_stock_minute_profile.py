from dataclasses import replace
from datetime import date, datetime
from unittest import TestCase

from app.core.market_time import CHINA, midnight
from app.models.kline.model import Candle
from app.services.minute_quality import MinuteCoverageError
from app.core.market_time import minute_window
from app.services.minute_quality import validate_minutes


FRIDAY = date(2026, 11, 20)
MONDAY = date(2026, 11, 23)
TUESDAY = date(2026, 11, 24)


def time_at(day, hour, minute=0, second=0):
    return int(datetime(day.year, day.month, day.day, hour, minute, second, tzinfo=CHINA).timestamp())


def bar(stamp, volume=100):
    return Candle(stamp, stamp + 60, 10, 11, 9, 10, volume, None, "shares", volume, adjustment="qfq")


def daily(day):
    return replace(bar(midnight(day)), end_timestamp=midnight(day) + 86400)


class MinuteQualityTests(TestCase):
    def test_partial_ends_round_out_and_lunch_and_auction_are_not_missing(self):
        raw_start = time_at(MONDAY, 11, 29, 53)
        raw_end = time_at(MONDAY, 13, 0, 2)
        start, end = minute_window(raw_start, raw_end)
        self.assertEqual((start, end), (time_at(MONDAY, 11, 29), time_at(MONDAY, 13, 1)))
        bars = (bar(start), bar(end - 60))
        selected, quality = validate_minutes(bars, start, end, (MONDAY,), (daily(MONDAY),), "demo")
        self.assertEqual(selected, bars)
        self.assertEqual(quality["minute_count"], 2)

        start, end = time_at(MONDAY, 14, 56), time_at(MONDAY, 15)
        rows = (bar(start), bar(end - 60))
        self.assertTrue(validate_minutes(rows, start, end, (MONDAY,), (daily(MONDAY),), "demo")[1]["complete"])

    def test_multiple_trading_days_using_calendar_skip_holidays_and_weekends(self):
        start = time_at(FRIDAY, 14, 59)
        end = time_at(TUESDAY, 9, 31)
        rows = (bar(start), bar(end - 60))
        data, quality = validate_minutes(rows, start, end, (FRIDAY, TUESDAY), (daily(FRIDAY), daily(TUESDAY)), "demo")
        self.assertEqual(len(data), 2)
        self.assertEqual(quality["trading_day_count"], 2)

    def test_missing_minute_does_not_get_filled(self):
        start, end = time_at(MONDAY, 9, 30), time_at(MONDAY, 9, 33)
        with self.assertRaises(MinuteCoverageError) as caught:
            validate_minutes((bar(start), bar(end - 60)), start, end, (MONDAY,), (daily(MONDAY),), "demo")
        self.assertEqual(caught.exception.quality["missing_minute_count"], 1)
        self.assertEqual(caught.exception.quality["available_start"], start)

    def test_duplicate_bad_ohlc_negative_volume_unclear_unit_and_unaligned_time(self):
        start = time_at(MONDAY, 9, 30)
        valid = bar(start)
        for bad, counter in (
            ((valid, valid), "duplicate_count"),
            ((replace(valid, low=20),), "invalid_count"),
            ((replace(valid, volume=-1),), "invalid_count"),
            ((replace(valid, original_volume_unit="unknown"),), "invalid_count"),
            ((replace(valid, original_volume_unit="rounded_lots", original_volume=1),), "invalid_count"),
            ((replace(valid, amount=-10),), "invalid_count"),
            ((replace(valid, original_volume=1),), "invalid_count"),
            ((replace(valid, timestamp=start + 5),), "invalid_count"),
            ((replace(valid, high=11.5),), "invalid_count"),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(MinuteCoverageError) as caught:
                    validate_minutes(bad, start, start + 60, (MONDAY,), (daily(MONDAY),), "demo")
                self.assertEqual(caught.exception.quality[counter], 1)

    def test_raw_turnover_is_not_compared_to_adjusted_prices(self):
        start = time_at(MONDAY, 9, 30)
        adjusted = replace(bar(start), amount=2000)
        selected, _ = validate_minutes((adjusted,), start, start + 60, (MONDAY,), (daily(MONDAY),), "demo")
        self.assertEqual(selected, (adjusted,))

    def test_no_trading_minutes_and_empty_snapshot_report_coverage(self):
        start, end = time_at(MONDAY, 12), time_at(MONDAY, 12, 30)
        with self.assertRaisesRegex(MinuteCoverageError, "没有交易分钟"):
            validate_minutes((), start, end, (MONDAY,), (daily(MONDAY),), "demo")
        start, end = time_at(MONDAY, 9, 30), time_at(MONDAY, 9, 31)
        with self.assertRaises(MinuteCoverageError) as caught:
            validate_minutes((), start, end, (MONDAY,), (daily(MONDAY),), "demo")
        self.assertIsNone(caught.exception.quality["available_start"])
        self.assertEqual(caught.exception.quality["missing_minute_count"], 1)

    def test_full_session_cross_checks_share_totals_against_daily_reference(self):
        start, end = time_at(MONDAY, 9, 30), time_at(MONDAY, 15)
        stamps = (
            *range(start, time_at(MONDAY, 11, 30), 60),
            *range(time_at(MONDAY, 13), time_at(MONDAY, 14, 57), 60),
            end - 60,
        )
        rows = tuple(bar(stamp) for stamp in stamps)
        day = replace(daily(MONDAY), volume=23_800)
        self.assertTrue(validate_minutes(rows, start, end, (MONDAY,), (day,), "demo")[1]["complete"])
        with self.assertRaises(MinuteCoverageError) as caught:
            validate_minutes(rows, start, end, (MONDAY,), (replace(day, volume=23_700),), "demo")
        self.assertEqual(caught.exception.quality["daily_mismatches"], [MONDAY.isoformat()])

    def test_native_hundred_share_granularity_has_bounded_daily_reconciliation(self):
        start, end = time_at(MONDAY, 9, 30), time_at(MONDAY, 15)
        stamps = (
            *range(start, time_at(MONDAY, 11, 30), 60),
            *range(time_at(MONDAY, 13), time_at(MONDAY, 14, 57), 60),
            end - 60,
        )
        rows = tuple(replace(bar(stamp), volume_precision_shares=100) for stamp in stamps)
        day = replace(daily(MONDAY), volume=23_849)
        _, quality = validate_minutes(rows, start, end, (MONDAY,), (day,), "easy-tdx-mac")
        self.assertEqual(quality["volume_precision_shares"], 100)
        with self.assertRaises(MinuteCoverageError):
            validate_minutes(rows, start, end, (MONDAY,), (replace(day, volume=23_900),), "easy-tdx-mac")
