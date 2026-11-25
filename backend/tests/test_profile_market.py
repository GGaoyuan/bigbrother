"""Exercise the simulated historical market data API through FastAPI."""

import io
import json
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from main import app


SHANGHAI = ZoneInfo("Asia/Shanghai")
BASE = "/api/v1/market/profile"


class ProfileMarketTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def request(self, route, **params):
        with redirect_stdout(io.StringIO()):
            return self.client.get(f"{BASE}/{route}", params=params)

    def data(self, route, **params):
        response = self.request(route, **params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 200)
        data = response.json()["data"]
        self.assertEqual(data["source"], "simulated")
        return data

    def test_history_has_full_overview_and_five_independent_periods(self):
        daily = self.data("history", code="000001", period="day")
        self.assertEqual((daily["code"], daily["name"]), ("000001", "平安银行"))
        self.assertGreater(daily["overview"][-1]["end"] - daily["overview"][0]["start"], 365 * 86400)
        self.assertEqual(daily["overview"], [
            {key: bar[key] for key in ("start", "end", "close")} for bar in daily["bars"]
        ])

        for period, count in (("60m", 4), ("30m", 8), ("15m", 16), ("5m", 48)):
            with self.subTest(period=period):
                history = self.data("history", code="000001", period=period)
                self.assertEqual(history["overview"], daily["overview"])
                bars = history["bars"]
                starts = [bar["start"] for bar in bars]
                self.assertEqual(starts, sorted(set(starts)))
                self.assertEqual(len(bars), count * len(daily["bars"]))
                last_session = bars[-count:]
                self.assertEqual(sum(bar["volume"] for bar in last_session), daily["bars"][-1]["volume"])
                self.assertEqual(last_session[-1]["close"], daily["bars"][-1]["close"])
                self.assertEqual(datetime.fromtimestamp(last_session[0]["start"], SHANGHAI).strftime("%H:%M"), "09:30")
                self.assertEqual(datetime.fromtimestamp(last_session[count // 2 - 1]["end"], SHANGHAI).strftime("%H:%M"), "11:30")
                self.assertEqual(datetime.fromtimestamp(last_session[count // 2]["start"], SHANGHAI).strftime("%H:%M"), "13:00")
                self.assertEqual(datetime.fromtimestamp(last_session[-1]["end"], SHANGHAI).strftime("%H:%M"), "15:00")

    def test_trades_are_deterministic_and_match_candlestick_exactly(self):
        last_bar = self.data("history", code="600519", period="5m")["bars"][-1]
        query = {"code": "600519", "start": last_bar["start"], "end": last_bar["end"]}
        trades = self.data("trades", **query)["trades"]
        self.assertEqual(trades, self.data("trades", **query)["trades"])
        self.assertEqual(trades[0]["time"], query["start"])
        self.assertTrue(all(query["start"] <= trade["time"] < query["end"] for trade in trades))
        self.assertTrue(all(trade["side"] in ("buy", "sell", "neutral", None) for trade in trades))
        prices = [trade["priceCents"] for trade in trades]
        self.assertEqual((prices[0], max(prices), min(prices), prices[-1]), (
            last_bar["open"], last_bar["high"], last_bar["low"], last_bar["close"],
        ))
        self.assertEqual(sum(trade["volume"] for trade in trades), last_bar["volume"])

        exclusive = self.data("trades", code="600519", start=trades[0]["time"], end=trades[1]["time"])
        self.assertEqual(exclusive["trades"], [trades[0]])

    def test_invalid_queries_use_422_envelope_and_empty_range_is_valid(self):
        for route, params in (
            ("history", {"code": "1", "period": "day"}),
            ("history", {"code": "000001", "period": "1m"}),
            ("trades", {"code": "000001", "start": 11, "end": 11}),
            ("trades", {"code": "000001", "start": -1, "end": 11}),
        ):
            with self.subTest(route=route, params=params):
                response = self.request(route, **params)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["code"], 422)

        self.assertEqual(self.data("trades", code="000001", start=0, end=100)["trades"], [])

    def test_data_source_error_uses_502_envelope(self):
        with patch("app.api.profile_market.get_history", side_effect=RuntimeError("provider")):
            response = self.request("history", code="000001", period="day")
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["code"], 502)

    def test_large_market_payload_is_logged_in_full(self):
        output = io.StringIO()
        with redirect_stdout(output):
            response = self.client.get(f"{BASE}/history", params={"code": "000001", "period": "5m"})

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()["data"]["bars"]), 10000)
        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(events[-1]["event"], "http.response")
        self.assertEqual(events[-1]["data"], response.json())
        self.assertEqual(events[-1]["bodyBytes"], len(response.content))
