import json
from typing import Any

from app.cache.base import Cache


class JsonCache(Cache):
    """JSON 缓存。dict / list / 标量等任意可 JSON 序列化的对象。

    使用：
        from app.cache import json_cache, CacheTTL
        await json_cache.set("k", {"a": 1}, ttl=CacheTTL.DAILY)
        data = await json_cache.get("k")
    """

    _content_type = "json"

    def _encode(self, value: Any) -> bytes:
        return json.dumps(value, ensure_ascii=False, default=str).encode("utf-8")

    def _decode(self, data: bytes) -> Any:
        return json.loads(data.decode("utf-8"))


json_cache = JsonCache()
