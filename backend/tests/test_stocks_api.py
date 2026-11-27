import io
from contextlib import redirect_stdout
from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from main import app
from test_stock_market import END, MINUTE_BARS, MINUTE_END, MINUTE_START, START, SYMBOL, fake_provider, stock_service


BASE = f"/api/v1/stocks/{SYMBOL}"


class StocksApiTests(TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.provider = fake_provider("easy-tdx")
        self.market, self.minute = stock_service(self.provider)
        patcher = patch.object(app, "state", self.market)
        patcher.start()
        self.addCleanup(patcher.stop)

    def request(self, route="", method="GET", **kwargs):
        with redirect_stdout(io.StringIO()):
            return self.client.request(method, BASE + route, **kwargs)

    def test_stock_market_and_normalized_history_contract(self):
        info = self.request().json()["data"]
        self.assertEqual((info["symbol"], info["exchange"], info["source"]), (SYMBOL, "SSE", "easy-tdx"))
        data = self.request("/klines", "POST", json={"interval": "5m"}).json()["data"]
        self.assertEqual((data["volume_unit"], data["adjust"], data["timezone"]), ("shares", "qfq", "Asia/Shanghai"))
        self.assertEqual(data["bars"][0]["timestamp"], START)
        self.assertEqual(data["bars"][0]["end_timestamp"], END)

    def test_klines_accepts_post_body_and_uses_cursor_as_the_upper_bound(self):
        default = self.request("/klines", "POST")
        self.assertEqual(default.json()["data"]["interval"], "1d")
        self.assertEqual(self.request("/klines").status_code, 405)

        response = self.request(
            "/klines", "POST", json={"start": START - 60, "end": END, "cursor": END - 60, "limit": 1},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["next_cursor"], START)
        self.market.klines.source.get_klines.assert_called_with(SYMBOL, "day", "none", START - 60, END - 60, 1)
        self.assertEqual(self.request(
            "/klines", "POST", json={"start": START, "end": END, "cursor": START},
        ).status_code, 422)

    def test_only_volume_profile_page_endpoints_are_registered(self):
        operations = [
            (method, route.path)
            for route in app.routes
            if isinstance(route, APIRoute)
            for method in route.methods
        ]
        self.assertCountEqual(operations, [
            ("GET", "/api/v1/stocks/{symbol}"),
            ("POST", "/api/v1/stocks/{symbol}/klines"),
            ("POST", "/api/v1/stocks/{symbol}/volume-profile"),
        ])

    def test_profile_is_independent_of_the_chart_period(self):
        results = []
        for period in ("1d", "60m", "5m"):
            chart = self.request("/klines", "POST", json={"interval": period}).json()["data"]
            response = self.request(
                "/volume-profile", "POST", json={"start": MINUTE_START, "end": MINUTE_END},
            )
            self.assertEqual(response.status_code, 200)
            profile = response.json()["data"]
            self.assertEqual(profile["profile"]["poc"]["priceCents"], 10100)
            self.assertEqual(profile["calculation_method"], "estimated_1m_weighted_range")
            self.assertEqual(profile["source"], chart["source"])
            self.assertEqual(profile["adjustment_version"], chart["adjustment_version"])
            self.assertEqual(profile["total_volume"], 200)
            self.assertEqual(profile["data_quality"]["minute_count"], 2)
            results.append(profile)
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])

    def test_profile_preserves_reported_share_precision(self):
        self.minute.get_klines.return_value = tuple(
            replace(bar, volume=100, original_volume=100, volume_precision_shares=100, amount=None)
            for bar in MINUTE_BARS
        )
        response = self.request(
            "/volume-profile", "POST", json={"start": MINUTE_START, "end": MINUTE_END},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["data_quality"]["volume_precision_shares"], 100)
        self.assertEqual(data["total_volume"], 200)
        self.assertTrue(any("100 股粒度" in warning for warning in data["warnings"]))

    def test_incomplete_profile_api_has_structured_quality(self):
        self.minute.get_klines.return_value = ()
        response = self.request(
            "/volume-profile", "POST", json={"start": MINUTE_START, "end": MINUTE_END},
        )
        self.assertEqual(response.status_code, 409)
        quality = response.json()["data"]["data_quality"]
        self.assertFalse(quality["complete"])
        self.assertEqual(quality["requested_start"], MINUTE_START)

    def test_invalid_code_ranges_adjustment_and_no_approximation_mode(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(self.client.get("/api/v1/stocks/123abc").status_code, 422)
            self.assertEqual(self.client.get("/api/v1/stocks/999999").status_code, 404)
        self.assertEqual(self.request("/klines", "POST", json={"adjust": "none"}).status_code, 422)
        for period in ("day", "1m", "15m", "30m"):
            self.assertEqual(self.request("/klines", "POST", json={"interval": period}).status_code, 422)
        self.assertEqual(self.request(
            "/volume-profile", "POST", json={"start": START, "end": END, "data_mode": "approximate"},
        ).status_code, 422)
