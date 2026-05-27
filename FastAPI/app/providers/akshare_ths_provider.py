import asyncio
import random
import time

import akshare as ak
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from typing import List
from urllib3.util.retry import Retry


def _patch_akshare_session(proxy=None):
    """
    给 akshare 的 request_with_retry 打补丁，添加浏览器 headers 和更强重试策略。
    针对东方财富接口的反爬机制优化。

    参数:
        proxy: 代理地址，格式如 "http://127.0.0.1:7890" 或 "socks5://127.0.0.1:1080"
    """
    import akshare.utils.request as ak_req
    import os

    _original = ak_req.request_with_retry

    _headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://quote.eastmoney.com/",
        "Connection": "keep-alive",
    }

    # 从环境变量或参数获取代理
    _proxy = proxy or os.getenv("AKSHARE_PROXY")
    _proxies = {"http": _proxy, "https": _proxy} if _proxy else None

    def _patched_request_with_retry(url, params=None, timeout=30,
                                    max_retries=5, base_delay=2.0,
                                    random_delay_range=(1.0, 3.0),
                                    **kwargs):
        last_exception = None
        for attempt in range(max_retries):
            try:
                session = requests.Session()
                session.headers.update(_headers)

                # 设置代理
                if _proxies:
                    session.proxies.update(_proxies)

                retry = Retry(
                    total=3,
                    backoff_factor=1.0,
                    status_forcelist=[500, 502, 503, 504],
                    allowed_methods=["GET", "POST"]
                )
                adapter = HTTPAdapter(
                    max_retries=retry,
                    pool_connections=10,
                    pool_maxsize=20
                )
                session.mount("http://", adapter)
                session.mount("https://", adapter)

                # 添加随机延迟，模拟人类行为
                if attempt > 0:
                    delay = base_delay * (2 ** attempt) + random.uniform(*random_delay_range)
                    time.sleep(delay)

                resp = session.get(url, params=params, timeout=timeout)
                resp.raise_for_status()
                session.close()
                return resp
            except (requests.RequestException, ValueError) as e:
                last_exception = e
                if hasattr(session, 'close'):
                    session.close()
        raise last_exception

    ak_req.request_with_retry = _patched_request_with_retry


_patch_akshare_session()

#
# async def get_concept_board_list() -> pd.DataFrame:
#     """
#     获取同花顺概念板块列表（名称+代码）。
#     """
#     df = await asyncio.to_thread(ak.stock_board_concept_name_ths)
#     if df is None or df.empty:
#         return pd.DataFrame()
#     return df
#
#
# async def get_industry_board_list() -> pd.DataFrame:
#     """
#     获取同花顺行业板块列表（名称+代码）。
#     """
#     df = await asyncio.to_thread(ak.stock_board_industry_name_ths)
#     if df is None or df.empty:
#         return pd.DataFrame()
#     return df