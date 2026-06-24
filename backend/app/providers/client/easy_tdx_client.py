"""easy_tdx 客户端工具 — 提供复用的 MacClient 连接。

MacClient 走通达信 Mac/扩展行情协议，不经东财节点，环境下稳定。
全市场快照、板块列表、行情排序筛选都用它。

懒加载单例：首次使用时连接最优服务器，后续复用。
"""

import threading

from easy_tdx import MacClient

_client: MacClient | None = None
_lock = threading.Lock()


def get_mac_client() -> MacClient:
    """获取复用的 MacClient（懒加载单例，线程安全）。"""
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = MacClient.from_best_host(timeout=10)
    return _client
