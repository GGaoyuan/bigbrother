"""Data source contracts shared by the service and data layers."""

from typing import Protocol

from app.models.calendar import TradingCalendar
from app.models.corporate_action import CorporateAction
from app.models.kline import Adjustment, Candle, Interval
from app.models.stock import StockInfo


class StockDataSource(Protocol):
    """Look up an exchange-listed A-share using its six-digit symbol."""

    name: str
    version: str

    def get_stock_info(self, symbol: str) -> StockInfo: ...


class KlineDataSource(Protocol):
    """Return standard candles in timestamp order using the requested price basis."""

    name: str
    version: str
    minute_history_limit: int | None  # None means the source accepts date-bounded pagination.

    def get_klines(
        self, symbol: str, interval: Interval, adjust: Adjustment,
        start: int | None, end: int | None, limit: int,
    ) -> tuple[Candle, ...]:
        """Query a half-open Unix-second window, keeping up to the latest limit bars."""
        ...


class CorporateActionDataSource(Protocol):
    """Normalize corporate actions used to compute a common price basis."""

    name: str
    version: str

    def get_corporate_actions(self, symbol: str) -> tuple[CorporateAction, ...]: ...


class CalendarDataSource(Protocol):
    """Supply covered dates and actual trading sessions."""

    name: str
    version: str

    def get_calendar(self) -> TradingCalendar: ...
