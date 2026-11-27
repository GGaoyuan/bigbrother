"""提供行情主站连接和同源重试。"""

from collections.abc import Callable
from time import monotonic
from typing import TypeVar

from app.core.exceptions import ProviderUnavailable


MAC_SERVERS = ("121.36.248.138", "123.60.47.136", "121.37.207.165")
QUERY_TIMEOUT = 18
Result = TypeVar("Result")


def fetch_market_data(
    client_type: Callable, servers: tuple[str, ...], operation: str,
    read: Callable[..., Result],
) -> Result:
    deadline = monotonic() + QUERY_TIMEOUT
    last_error = None
    for host in servers:
        remaining = deadline - monotonic()
        if remaining <= 0:
            break
        try:
            with client_type(
                host, port=7709, timeout=min(3, remaining), auto_reconnect=False, heartbeat_interval=0,
            ) as client:
                return read(client, deadline)
        except Exception as exc:
            last_error = exc
    detail = f"：{last_error}" if last_error else ""
    raise ProviderUnavailable(f"通达信{operation}暂不可用{detail}") from last_error
