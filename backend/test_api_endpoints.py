"""逐个隔离测试 API 接口，避免 py_mini_racer 崩溃影响全部结果。"""
import json
import subprocess
import sys
import textwrap

AUTH_HEADERS = '{"token": "gaoyuanzuishuai", "uid": "1993"}'

ENDPOINTS = [
    ("GET", "/", None),
    ("GET", "/health", None),
    ("POST", "/api/v1/market/index/core", {}),
    ("POST", "/api/v1/market/index/spot", {}),
    ("POST", "/api/v1/market/index/style", {}),
    ("POST", "/api/v1/market/index/hist", {"symbol": "000001", "index_name": "上证指数"}),
    ("POST", "/api/v1/breadth/volume", {}),
    ("POST", "/api/v1/breadth/limit-pools", {}),
    ("POST", "/api/v1/breadth/fund-flow-rank", {"indicator": "今日"}),
    ("POST", "/api/v1/sector/realtime", {"type": 3}),
    ("POST", "/api/v1/sector/fund-flow", {"indicator": "今日", "sector_type": "行业资金流"}),
    ("POST", "/api/v1/sector/ths-fund-flow", {}),
    ("POST", "/api/v1/sector/sw-industry", {}),
    ("POST", "/api/v1/sector/sw-stock-industry", {}),
    ("POST", "/api/v1/capital/northbound", {}),
    ("POST", "/api/v1/capital/margin", {}),
    ("POST", "/api/v1/capital/dragon-tiger", {}),
    ("POST", "/api/v1/capital/market-flow", {}),
    ("POST", "/api/v1/news/overview", {}),
    ("POST", "/api/v1/analysis/dashboard", {}),
    ("POST", "/api/v1/forward", {"source": "akshare", "fn": "stock_sse_summary", "param": {}}),
]


def _worker_code(method: str, path: str, body) -> str:
    body_json = json.dumps(body, ensure_ascii=False)
    return textwrap.dedent(
        f"""
        import json, time
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)
        headers = json.loads({json.dumps(AUTH_HEADERS)})
        body = json.loads({json.dumps(body_json)})
        started = time.time()
        try:
            if {json.dumps(method)} == "GET":
                resp = client.get({json.dumps(path)}, headers=headers)
            else:
                resp = client.post({json.dumps(path)}, json=body, headers=headers)
            elapsed = round(time.time() - started, 2)
            payload = resp.json()
            code = payload.get("code")
            data = payload.get("data")
            ok = resp.status_code == 200 and code == 200 and data not in (None, [], {{}})
            if isinstance(data, dict) and not data:
                ok = False
            summary = None
            if isinstance(data, list):
                summary = f"list[{{len(data)}}]"
            elif isinstance(data, dict):
                parts = []
                for k, v in list(data.items())[:5]:
                    if isinstance(v, list):
                        parts.append(f"{{k}}:list[{{len(v)}}]")
                    elif isinstance(v, dict):
                        parts.append(f"{{k}}:dict[{{len(v)}}]")
                    else:
                        parts.append(f"{{k}}:{{type(v).__name__}}")
                summary = "{{" + ", ".join(parts) + "}}"
            print(json.dumps({{
                "status": "ok" if ok else "fail",
                "http_status": resp.status_code,
                "api_code": code,
                "message": payload.get("message"),
                "elapsed_s": elapsed,
                "summary": summary,
                "error": None if ok else payload.get("message") or "空数据",
            }}, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({{
                "status": "fail",
                "elapsed_s": round(time.time() - started, 2),
                "error": str(e)[:300],
            }}, ensure_ascii=False))
        """
    )


def main():
    results = []
    python = sys.executable
    for method, path, body in ENDPOINTS:
        print(f"testing {path} ...", flush=True)
        proc = subprocess.run(
            [python, "-c", _worker_code(method, path, body)],
            cwd="/Users/admin/Desktop/gy/bigbrother/backend",
            capture_output=True,
            text=True,
            timeout=180,
        )
        item = {"path": path, "method": method}
        if proc.returncode != 0:
            item.update(
                {
                    "status": "fail",
                    "error": (proc.stderr or proc.stdout or "进程崩溃")[:400],
                    "exit_code": proc.returncode,
                }
            )
        else:
            line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
            try:
                item.update(json.loads(line))
            except json.JSONDecodeError:
                item.update({"status": "fail", "error": proc.stdout[:400]})
        results.append(item)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
