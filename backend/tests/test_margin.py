"""两融汇总接口测试；仅替换交易所 HTTP 传输。"""

import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from types import SimpleNamespace
from urllib.parse import urlparse
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


def sse_row(day, balance, purchase, repayment):
    return dict(ROWNUM_=None, opDate=day, rqchl=None, rqmcl=10000, rqyl=20000,
                rqylje=2000000, rw=None, rzche=repayment, rzmre=purchase,
                rzrqjyzl=balance + 2000000, rzye=balance,
                securityAbbr=None, stockCode=None)


class MarginTests(unittest.TestCase):
    def setUp(self):
        self.sse = [sse_row("20261106", 100000000, 10000000, 2000000),
                    sse_row("20261109", 110000000, 13000000, 3000000)]
        self.szse = {
            "2026-11-06": self.report("2026-11-06", "2.00"),
            "2026-11-09": self.report("2026-11-09", "2.20"),
        }
        self.calls = []
        clock = patch("app.api.margin.datetime")
        clock.start().now.return_value = datetime(2026, 11, 10)
        self.addCleanup(clock.stop)
        transport = patch("akshare.utils.http.get", side_effect=self.get)
        transport.start()
        self.addCleanup(transport.stop)
        direct_http = patch("urllib.request.urlopen", side_effect=AssertionError("禁止自行抓取"))
        direct_http.start()
        self.addCleanup(direct_http.stop)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    @staticmethod
    def report(day, balance):
        return [{"metadata": {"subname": day, "tabkey": "tab1", "cols": {
            "jrrzmr": "融资买入额<br>(亿元)", "jrrzye": "融资余额<br>(亿元)",
            "jrrjmc": "融券卖出量<br>(亿股/亿份)", "jrrjyl": "融券余量<br>(亿股/亿份)",
            "jrrjye": "融券余额<br>(亿元)", "jrrzrjye": "融资融券余额<br>(亿元)",
        }}, "data": [{"jrrzmr": "0.30", "jrrzye": balance, "jrrjmc": "0.01",
                       "jrrjyl": "0.02", "jrrjye": "0.05", "jrrzrjye": "2.25"}],
                 "error": None}]

    def get(self, request_url, params, **kwargs):
        url = urlparse(request_url)
        query = params
        self.calls.append((url.hostname, query))
        if url.hostname == "query.sse.com.cn":
            data = {"result": self.sse, "pageHelp": {"pageCount": 1}}
        elif url.hostname == "www.szse.cn":
            data = self.szse.get(query["txtDate"], [{
                "metadata": {"subname": "", "tabkey": "tab1"}, "data": [], "error": None,
            }])
        else:
            raise AssertionError("Unexpected data source")
        return SimpleNamespace(json=lambda: data)

    def request(self, body=None, authenticated=True):
        headers = {"Authorization": "Bearer mock-token-10001"} if authenticated else {}
        with redirect_stdout(io.StringIO()):
            return self.client.post("/api/v1/capital/margin", json=body, headers=headers)

    def test_combines_same_day_and_converts_szse_units(self):
        response = self.request({"date": "2026-11-09"})
        self.assertEqual(response.status_code, 200)
        row = response.json()["data"][0]
        self.assertEqual(row["trade_date"], "2026-11-09")
        self.assertEqual(row["sse"]["financing_balance"], 110000000)
        self.assertEqual(row["szse"]["financing_balance"], 220000000)
        self.assertEqual(row["total"]["financing_balance"], 330000000)
        self.assertEqual(row["total"]["securities_sold_volume"], 1010000)
        self.assertEqual(row["total"]["financing_repayment_amount"], 13000000)
        self.assertTrue(row["szse"]["financing_repayment_estimated"])
        self.assertEqual(row["szse"]["amount_precision"], 1000000)

    def test_latest_uses_latest_common_date_not_mixed_dates(self):
        self.szse.pop("2026-11-09")
        response = self.request()
        self.assertEqual(response.status_code, 200)
        row = response.json()["data"][0]
        self.assertEqual(row["trade_date"], "2026-11-06")
        self.assertEqual(row["total"]["financing_balance"], 300000000)
        self.assertIsNone(row["total"]["financing_repayment_amount"])

    def test_specified_non_trading_day_returns_empty(self):
        self.assertEqual(self.request({"date": "2026-11-08"}).json()["data"], [])

    def test_empty_sse_window_returns_empty(self):
        self.sse = []
        response = self.request({"date": "2026-11-09"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_multiple_szse_rows_are_rejected(self):
        self.szse["2026-11-09"][0]["data"] *= 2
        self.assertEqual(self.request({"date": "2026-11-09"}).status_code, 502)

    def test_missing_value_is_not_fabricated_as_zero(self):
        self.szse["2026-11-09"][0]["data"][0]["jrrzye"] = "--"
        self.assertEqual(self.request({"date": "2026-11-09"}).status_code, 502)

    def test_missing_szse_does_not_return_partial_total(self):
        self.szse.clear()
        self.assertEqual(self.request({"date": "2026-11-09"}).json()["data"], [])

    def test_invalid_date_is_rejected_without_fetch(self):
        self.assertEqual(self.request({"date": "2026-02-30"}).status_code, 422)
        self.assertEqual(self.calls, [])

    def test_authentication_required(self):
        self.assertEqual(self.request(authenticated=False).status_code, 401)
        self.assertEqual(self.calls, [])

    def test_upstream_error_returns_bad_gateway(self):
        with patch("akshare.utils.http.get", side_effect=OSError("unavailable")):
            self.assertEqual(self.request({"date": "2026-11-09"}).status_code, 502)

    def test_latest_excludes_sixty_first_day(self):
        self.sse = [sse_row("20260911", 100000000, 10000000, 2000000)]
        self.szse = {"2026-09-11": self.report("2026-09-11", "2.00")}
        with patch("app.api.margin.datetime") as clock:
            clock.now.return_value = datetime(2026, 11, 10)
            response = self.request()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_unexpected_akshare_shape_error_is_not_treated_as_no_data(self):
        self.szse["2026-11-09"][0]["data"][0]["new_field"] = "unexpected"
        self.assertEqual(self.request({"date": "2026-11-09"}).status_code, 502)
