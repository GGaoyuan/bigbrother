import asyncio
import efinance as ef
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _patch_ef_session():
    """
    给 efinance 内部的 session 打补丁，解决东方财富 RemoteDisconnected 问题：
    1. 禁用 keep-alive（Connection: close），避免长连接被服务器主动断开
    2. 加重试 adapter，遇到断连自动重试
    3. 设置浏览器 User-Agent，绕过基础反爬
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://quote.eastmoney.com/",
        "Connection": "close",  # 禁用 keep-alive
    }

    retry = Retry(
        total=5,
        backoff_factor=0.8,                         # 间隔 0.8s, 1.6s, 3.2s ...
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)

    # efinance 0.4+ 把 session 放在 ef.shared.session
    sessions = []
    if hasattr(ef, "session"):
        sessions.append(ef.session)
    try:
        from efinance.shared import session as shared_session  # type: ignore
        sessions.append(shared_session)
    except Exception:
        pass

    for s in sessions:
        s.headers.update(headers)
        s.mount("http://", adapter)
        s.mount("https://", adapter)


_patch_ef_session()


async def get_today_capital_flow(code: str) -> pd.DataFrame:
    """
    获取单只股票/板块最新交易日的日内分钟级资金流入流出数据。

    Args:
        code: 股票代码或板块代码，如 "600519"、"000001"、"BK0457"
    """
    df = await asyncio.to_thread(ef.stock.get_today_bill, code)

    if df is None or df.empty:
        return pd.DataFrame()

    return df
