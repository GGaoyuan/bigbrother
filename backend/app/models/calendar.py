from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class TradingCalendar:
    """Inclusive validity bounds and actual (sorted) trading dates."""

    start: date
    end: date
    sessions: tuple[date, ...]
