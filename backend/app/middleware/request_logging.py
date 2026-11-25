"""Record HTTP inputs and the full response around the complete ASGI stack."""

import json
from time import perf_counter
from urllib.parse import parse_qs
from uuid import uuid4

from app.console_logging import log_event, request_id


def _content_type(headers) -> str:
    return dict(headers).get(b"content-type", b"").decode("latin-1")


def _decode_payload(body: bytearray, content_type: str) -> object:
    if not body:
        return None
    text = body.decode("utf-8", errors="replace")
    if "application/x-www-form-urlencoded" in content_type:
        return parse_qs(text, keep_blank_values=True)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if "json" in content_type:
            return {"invalidJson": True, "bodyBytes": len(body)}
        return text


class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        context_token = request_id.set(uuid4().hex)
        started_at = perf_counter()
        method = scope["method"]
        path = scope["path"]
        request_body = bytearray()
        request_type = _content_type(scope.get("headers", ()))
        response_body = bytearray()
        response_type = ""
        status = None
        complete = False
        query = scope.get("query_string", b"").decode("utf-8", errors="replace")

        async def receive_with_capture():
            message = await receive()
            if message["type"] == "http.request":
                request_body.extend(message.get("body", b""))
                if request_body and not message.get("more_body", False):
                    log_event("http.request_body", method=method, path=path,
                              body=_decode_payload(request_body, request_type))
            return message

        async def send_with_capture(message):
            nonlocal status, response_type, complete
            if message["type"] == "http.response.start":
                status = message["status"]
                response_type = _content_type(message.get("headers", ()))
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))
                complete = not message.get("more_body", False)
            await send(message)

        try:
            log_event("http.request", method=method, path=path, queryParams=parse_qs(query, keep_blank_values=True))
            await self.app(scope, receive_with_capture, send_with_capture)
        finally:
            try:
                log_event(
                    "http.response", method=method, path=path, pathParams=scope.get("path_params", {}),
                    statusCode=status, durationMs=round((perf_counter() - started_at) * 1000, 2),
                    bodyBytes=len(response_body), complete=complete, data=_decode_payload(response_body, response_type),
                )
            finally:
                request_id.reset(context_token)
