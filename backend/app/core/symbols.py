"""Shared classification of six-digit A-share codes."""

from app.core.exceptions import StockNotFound


def stock_exchange(symbol: str) -> str:
    if len(symbol) != 6 or not symbol.isascii() or not symbol.isdigit():
        raise StockNotFound("请输入六位 A 股代码")
    if symbol.startswith(("600", "601", "603", "605", "688", "689")):
        return "SSE"
    if symbol.startswith(("000", "001", "002", "003", "300", "301")):
        return "SZSE"
    if symbol.startswith(("4", "8", "920")):
        return "BSE"
    raise StockNotFound(f"{symbol} 不属于支持的 A 股代码段")


def stock_board(symbol: str) -> str:
    if stock_exchange(symbol) == "BSE":
        return "北交所"
    if symbol.startswith(("688", "689")):
        return "科创板"
    if symbol.startswith(("300", "301")):
        return "创业板"
    return "主板"
