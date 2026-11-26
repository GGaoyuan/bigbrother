"""Adapt the installed exchange calendar to a validated A-share date range."""

from importlib.metadata import version

from exchange_calendars import get_calendar
from exchange_calendars.exchange_calendar_xshg import XSHGExchangeCalendar

from app.core.exceptions import ProviderUnavailable
from app.models.calendar import TradingCalendar


class XshgCalendarData:
    name = "exchange-calendars-xshg"
    version = version("exchange-calendars")

    def get_calendar(self) -> TradingCalendar:
        # The package's published bounds include non-trading days at either edge.
        start = XSHGExchangeCalendar.bound_min()
        end = XSHGExchangeCalendar.bound_max()
        try:
            calendar = get_calendar("XSHG", start=start, end=end)
            sessions = tuple(calendar.sessions.date)
        except (TypeError, ValueError, RuntimeError) as exc:
            raise ProviderUnavailable("交易日历暂不可用") from exc
        if not sessions or sessions != tuple(sorted(set(sessions))):
            raise ProviderUnavailable("交易日历返回日期无效")
        return TradingCalendar(start.date(), end.date(), sessions)
