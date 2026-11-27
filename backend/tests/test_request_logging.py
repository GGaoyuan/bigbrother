import io
import json
from contextlib import redirect_stdout
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.exceptions import ProviderUnavailable
from main import app
from test_stock_market import MINUTE_END, MINUTE_START, SYMBOL, fake_provider, mock_market


BASE = f"/api/v1/stocks/{SYMBOL}"


class RequestLoggingTests(TestCase):
    def setUp(self):
        self.client = TestClient(app, raise_server_exceptions=False)
        self.addCleanup(self.client.close)

    def request(self, method, route, **kwargs):
        output = io.StringIO()
        with redirect_stdout(output):
            response = self.client.request(method, route, **kwargs)
        return response, [json.loads(line) for line in output.getvalue().splitlines()]

    def test_provider_and_response_share_the_request_id_on_each_request(self):
        provider = fake_provider("easy-tdx")
        mock_market(self, provider)
        provider.get_stock_info.side_effect = ProviderUnavailable("连接超时")
        failed, failed_events = self.request("GET", BASE)
        provider.get_stock_info.side_effect = None
        response, events = self.request("GET", BASE, params={"lookup": "yes"})
        _, repeated = self.request("GET", BASE)

        self.assertEqual(failed.status_code, 502)
        self.assertTrue(any(event["event"] == "provider.failed" for event in failed_events))
        self.assertEqual(events[0]["event"], "http.request")
        self.assertEqual(events[0]["queryParams"], {"lookup": ["yes"]})
        self.assertEqual([(e["event"], e["provider"]) for e in events[1:-1]], [
            ("provider.attempt", "easy-tdx"),
            ("provider.selected", "easy-tdx"),
        ])
        self.assertEqual(events[-1]["pathParams"], {"symbol": SYMBOL})
        self.assertEqual(events[-1]["data"], response.json())
        self.assertEqual(len({event["requestId"] for event in events}), 1)
        self.assertNotEqual(repeated[0]["requestId"], events[0]["requestId"])
        self.assertEqual([event["event"] for event in repeated[1:-1]], ["provider.attempt", "provider.selected"])
        self.assertEqual(provider.get_stock_info.call_count, 3)

    def test_profile_logs_post_body_and_minute_source_before_the_full_result(self):
        mock_market(self, fake_provider("easy-tdx"))
        payload = {"start": MINUTE_START, "end": MINUTE_END}
        response, events = self.request("POST", BASE + "/volume-profile", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(events[1]["event"], "http.request_body")
        self.assertEqual(events[1]["body"], payload)
        minute = next(
            event for event in events
            if event["event"] == "provider.selected" and event["operation"] == "profile_minutes"
        )
        self.assertEqual((minute["provider"], minute["rowCount"]), ("easy-tdx", 2))
        self.assertEqual(events[-1]["data"], response.json())
        self.assertGreaterEqual(events[-1]["durationMs"], 0)

    def test_validation_failures_redact_nested_body_and_query_secrets(self):
        response, events = self.request(
            "POST", BASE + "/volume-profile",
            params={"token": "query-secret"}, json={"nested": {"password": "body-secret"}},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(events[0]["queryParams"], {"token": "[REDACTED]"})
        self.assertEqual(events[1]["body"], {"nested": {"password": "[REDACTED]"}})
        self.assertEqual(events[-1]["statusCode"], 422)
        self.assertEqual(events[-1]["data"], response.json())

    def test_preflight_not_found_and_server_errors_log_the_actual_http_response(self):
        preflight, events = self.request("OPTIONS", BASE, headers={
            "origin": "http://localhost:5173",
            "access-control-request-method": "GET",
        })
        self.assertEqual(events[-1]["statusCode"], preflight.status_code)
        self.assertEqual(events[-1]["data"], preflight.text)

        missing, events = self.request("GET", "/missing-log-test")
        self.assertEqual(events[-1]["statusCode"], 404)
        self.assertEqual(events[-1]["data"], missing.json())

        with patch("app.api.stock.get_stock", side_effect=RuntimeError("test failure")):
            failed, events = self.request("GET", BASE)
        self.assertEqual(events[-1]["statusCode"], 500)
        self.assertEqual(events[-1]["data"], failed.json())
