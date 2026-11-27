"""读取 XSHG 离线交易日历。"""

from importlib.metadata import version as package_version

from exchange_calendars import get_calendar
from exchange_calendars.exchange_calendar_xshg import XSHGExchangeCalendar

from app.core.exceptions import ProviderUnavailable

from .model import TradingCalendar


class TradingCalendarProvider:
    name = "exchange-calendars-xshg"
    version = package_version("exchange-calendars")

    def get_calendar(self) -> TradingCalendar:
        # 日历库声明的覆盖范围端点可能是非交易日。
        start = XSHGExchangeCalendar.bound_min()
        end = XSHGExchangeCalendar.bound_max()
        try:
            calendar = get_calendar("XSHG", start=start, end=end)
            sessions = tuple(calendar.sessions.date)
        except (TypeError, ValueError, RuntimeError) as exc:
            raise ProviderUnavailable("交易日历暂不可用") from exc
        return TradingCalendar(start.date(), end.date(), sessions)
