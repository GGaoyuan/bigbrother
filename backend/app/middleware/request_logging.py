import json
import time
from datetime import datetime
from urllib.parse import parse_qs

SENSITIVE_FIELDS = {
    "password",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "secret",
}


def _redact(value: object, field_name: str = "") -> object:
    if field_name.lower() in SENSITIVE_FIELDS:
        return "[REDACTED]"

    if isinstance(value, dict):
        return {
            key: _redact(item, str(key))
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_redact(item) for item in value]

    return value


def _decode_payload(body: bytes, content_type: str) -> object:
    if not body:
        return None

    text = body.decode("utf-8", errors="replace")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        if "application/x-www-form-urlencoded" in content_type:
            return _redact(parse_qs(text, keep_blank_values=True))
        return text

    return _redact(payload)


class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started_at = time.perf_counter()
        request_body = bytearray()
        response_body = bytearray()
        response_status = 500
        content_type = ""

        async def receive_with_capture():
            message = await receive()
            if message["type"] == "http.request":
                request_body.extend(message.get("body", b""))
            return message

        async def send_with_capture(message):
            nonlocal response_status, content_type

            if message["type"] == "http.response.start":
                response_status = message["status"]
                headers = dict(message.get("headers", []))
                content_type = headers.get(b"content-type", b"").decode(
                    "latin-1",
                    errors="replace",
                )

            if message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

            await send(message)

        try:
            await self.app(scope, receive_with_capture, send_with_capture)
        finally:
            query_string = scope.get("query_string", b"").decode(
                "utf-8",
                errors="replace",
            )
            query_params = parse_qs(query_string, keep_blank_values=True)
            request_headers = dict(scope.get("headers", []))
            request_content_type = request_headers.get(
                b"content-type",
                b"",
            ).decode("latin-1", errors="replace")

            request_data = {
                "method": scope.get("method", ""),
                "path": scope.get("path", ""),
                "pathParams": _redact(scope.get("path_params", {})),
                "queryParams": _redact(query_params),
                "body": _decode_payload(bytes(request_body), request_content_type),
            }
            response_data = _decode_payload(bytes(response_body), content_type)
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            log_entry = {
                "time": datetime.now().astimezone().isoformat(timespec="milliseconds"),
                "request": request_data,
                "response": {
                    "statusCode": response_status,
                    "data": response_data,
                },
                "durationMs": round(elapsed_ms, 2),
            }

            print(
                json.dumps(log_entry, ensure_ascii=False, indent=2, default=str),
                flush=True,
            )
