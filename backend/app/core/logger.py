"""将同一请求的事件以 JSON 格式输出到后端控制台。"""

import json
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from threading import Lock


request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_output_lock = Lock()
SENSITIVE_FIELDS = frozenset({
    "password", "passwd", "token", "accesstoken", "refreshtoken", "authorization",
    "secret", "clientsecret", "apikey", "cookie", "setcookie",
})


def redact(value: object, field: str = "") -> object:
    if field.casefold().replace("_", "").replace("-", "") in SENSITIVE_FIELDS:
        return "[REDACTED]"
    if isinstance(value, dict):
        return {key: redact(item, str(key)) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    return value


def log_event(event: str, **fields: object) -> None:
    current_id = request_id.get()
    if current_id is None:
        return

    entry = {
        "time": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        "requestId": current_id,
        "event": event,
        **fields,
    }
    line = json.dumps(redact(entry), ensure_ascii=False, default=str)
    with _output_lock:
        print(line, flush=True)


def log_provider(status: str, provider: str, operation: str, **fields: object) -> None:
    log_event(f"provider.{status}", provider=provider, operation=operation, **fields)


@contextmanager
def observe_provider(provider: str, operation: str, **parameters: object):
    log_provider("attempt", provider, operation, **parameters)
    try:
        yield
    except Exception as exc:
        log_provider("failed", provider, operation, errorType=type(exc).__name__, reason=str(exc), **parameters)
        raise
    else:
        log_provider("selected", provider, operation, **parameters)
