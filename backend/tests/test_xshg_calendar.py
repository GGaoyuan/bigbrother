from datetime import date, timedelta
from unittest import TestCase

from app.data.xshg_calendar import XshgCalendarData


class XshgCalendarTests(TestCase):
    def test_2026_national_day_closure_and_confirmed_session_range(self):
        calendar = XshgCalendarData().get_calendar()
        first = date(2026, 10, 1)
        closures = {first + timedelta(days=offset) for offset in range(7)}
        self.assertTrue(closures.isdisjoint(calendar.sessions))
        self.assertIn(date(2026, 9, 30), calendar.sessions)
        self.assertIn(date(2026, 10, 8), calendar.sessions)
        self.assertNotIn(date(2026, 10, 10), calendar.sessions)
        self.assertGreaterEqual(calendar.end, date(2026, 12, 31))
