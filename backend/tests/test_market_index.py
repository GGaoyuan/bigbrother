"""Exercise index requests with real mootdx conversion and a fake TDX transport."""

import logging
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from fastapi.testclient import TestClient
from mootdx.quotes import StdQuotes

from main import app


class TdxTransport:
    def __init__(self):
        self.calls = []
        self.error = None
        self.rows = [
            dict(datetime="2026-11-09 15:00", year=2026, month=11, day=9,
                 hour=15, minute=0, open=110, high=112, low=109, close=110,
                 vol=200, amount=22000),
            dict(datetime="2026-11-06 15:00", year=2026, month=11, day=6,
                 hour=15, minute=0, open=99, high=101, low=98, close=100,
                 vol=100, amount=10000),
        ]

    def get_index_bars(self, frequency, market, symbol, start, offset):
        self.calls.append((frequency, market, symbol, start, offset))
        if self.error:
            raise self.error
        return self.rows


class IndexDailyKlineTests(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging.NOTSET)
        self.transport = TdxTransport()
        quotes = object.__new__(StdQuotes)
        quotes.client = self.transport
        factory = patch("app.data.tdx._client", return_value=quotes)
        factory.start()
        self.addCleanup(factory.stop)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def request(self, body=None, authenticated=True):
        headers = {"Authorization": "Bearer mock-token-10001"} if authenticated else {}
        with redirect_stdout(io.StringIO()):
            return self.client.post("/api/v1/market/index/hist", json=body, headers=headers)

    def test_csi300_daily_bars_use_shanghai_index_and_chronological_prices(self):
        response = self.request({"code": "000300.SH"})
        self.assertEqual(response.status_code, 200)
        bars = response.json()["data"]
        self.assertEqual([row["trade_date"] for row in bars], ["2026-11-06", "2026-11-09"])
        self.assertEqual(bars[0]["close"], 100)
        self.assertEqual(bars[1]["volume"], 200)
        self.assertEqual(bars[1]["amount"], 22000)
        self.assertEqual(bars[1]["change_pct"], 10)
        self.assertEqual(self.transport.calls, [(9, 1, "000300", 0, 800)])

    def test_omitted_body_preserves_shanghai_default(self):
        response = self.request()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 2)
        self.assertEqual(self.transport.calls, [(9, 1, "000001", 0, 800)])

    def test_all_indices_use_fixed_count_even_if_legacy_limit_is_sent(self):
        for code in ["000001.SH", "000300.SH"]:
            with self.subTest(code=code):
                response = self.request({"code": code, "limit": 2})
                self.assertEqual(response.status_code, 200)
        self.assertEqual(self.transport.calls, [
            (9, 1, "000001", 0, 800), (9, 1, "000300", 0, 800),
        ])

    def test_invalid_codes_are_rejected_before_fetch(self):
        for body in [{"code": "600000.SH"}, {"code": "000300.SZ"}]:
            with self.subTest(body=body):
                self.assertEqual(self.request(body).status_code, 422)
        self.assertEqual(self.transport.calls, [])

    def test_upstream_failure_returns_bad_gateway(self):
        self.transport.error = ConnectionError("TDX unavailable")
        response = self.request({"code": "000300.SH"})
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["code"], 502)

    def test_empty_data_returns_empty_list(self):
        self.transport.rows = []
        self.assertEqual(self.request({"code": "000300.SH"}).json()["data"], [])

    def test_index_endpoint_requires_authentication(self):
        self.assertEqual(self.request({"code": "000300.SH"}, authenticated=False).status_code, 401)
        self.assertEqual(self.transport.calls, [])
