"""定义交易日历及其覆盖范围。"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class TradingCalendar:
    """定义含首尾日期的日历覆盖范围，以及按升序排列的实际交易日。"""

    start: date
    end: date
    sessions: tuple[date, ...]
