import csv
import io
from typing import List

from app.cache.base import Cache


class CsvCache(Cache):
    """CSV 缓存。专为 list[dict] 行集合设计。

    注意：CSV 格式不保留类型信息，所有值落盘后读回都是字符串。
    若需保留 int/float/None，请改用 JsonCache。

    使用：
        from app.cache import csv_cache, CacheTTL
        await csv_cache.set("k", [{"col": 1}], ttl=CacheTTL.WEEKLY)
        rows = await csv_cache.get("k")
    """

    _content_type = "csv"

    def _encode(self, rows: List[dict]) -> bytes:
        if not rows:
            return b""
        fieldnames: List[str] = list(rows[0].keys())
        for item in rows[1:]:
            for k in item:
                if k not in fieldnames:
                    fieldnames.append(k)
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue().encode("utf-8-sig")

    def _decode(self, data: bytes) -> List[dict]:
        if not data:
            return []
        text = data.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)


csv_cache = CsvCache()
