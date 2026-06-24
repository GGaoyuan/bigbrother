import asyncio
import hashlib
import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.cache.ttl import CacheTTL

# 项目根目录的 data/（与 backend/ 同级）：app/cache/client.py -> 上四层 = 项目根
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DEFAULT_CACHE_DIR = PROJECT_ROOT / "data"

# 文件名中不允许出现的字符，统一替换成 _
_UNSAFE_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]+')
_MAX_NAME_LEN = 120  # 超长 key 截断后挂哈希避免冲突


def _safe_name(key: str) -> str:
    """把 key 转成文件名安全形式。保留可读性，超长截断+哈希后缀。"""
    cleaned = _UNSAFE_CHARS.sub("_", key).strip("._")
    if not cleaned:
        cleaned = "_"
    if len(cleaned) > _MAX_NAME_LEN:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]
        cleaned = f"{cleaned[:_MAX_NAME_LEN - 9]}__{digest}"
    return cleaned


@dataclass
class CacheMeta:
    """缓存条目的元数据。"""

    key: str
    content_type: str  # 由子类的 _content_type 决定
    cached_at: datetime
    expires_at: datetime
    size: int


class Cache(ABC):
    """缓存抽象基类。

    通用逻辑（文件命名、原子写、meta 管理、过期判定、delete/clear）由本类实现，
    子类只需要实现：
      - _content_type：内容类型字符串，决定文件后缀（如 "json"、"csv"）
      - _encode(value) -> bytes：序列化
      - _decode(bytes) -> value：反序列化

    每个条目落两个文件：
      <safe_key>.<content_type>             负载
      <safe_key>.<content_type>.meta.json   元数据

    JsonCache 与 CsvCache 共用同一目录时，因 meta 文件名带 content_type 不会冲突。
    """

    def __init__(self, cache_dir: os.PathLike = DEFAULT_CACHE_DIR):
        self._cache_dir = Path(cache_dir)

    # ---------- 子类填充 ----------

    @property
    @abstractmethod
    def _content_type(self) -> str: ...

    @abstractmethod
    def _encode(self, value: Any) -> bytes: ...

    @abstractmethod
    def _decode(self, data: bytes) -> Any: ...

    # ---------- 路径与 meta ----------

    def _dir_for(self, namespace: str) -> Path:
        """根据 namespace 返回缓存子目录（namespace 为空时用根目录）。"""
        return self._cache_dir / namespace if namespace else self._cache_dir

    def _data_path(self, key: str, namespace: str = "") -> Path:
        return self._dir_for(namespace) / f"{_safe_name(key)}.{self._content_type}"

    def _meta_path(self, key: str, namespace: str = "") -> Path:
        return self._dir_for(namespace) / f"{_safe_name(key)}.{self._content_type}.meta.json"

    def _load_meta(self, key: str, namespace: str = "") -> Optional[CacheMeta]:
        path = self._meta_path(key, namespace)
        if not path.exists():
            return None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return CacheMeta(
                key=raw["key"],
                content_type=raw["content_type"],
                cached_at=datetime.fromisoformat(raw["cached_at"]),
                expires_at=datetime.fromisoformat(raw["expires_at"]),
                size=raw["size"],
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _atomic_write(self, path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, path)

    def _write_entry(self, key: str, payload: bytes, ttl: CacheTTL, namespace: str = "") -> None:
        now = datetime.now()
        expires_at = ttl.expires_at(now)
        self._atomic_write(self._data_path(key, namespace), payload)
        meta = {
            "key": key,
            "content_type": self._content_type,
            "cached_at": now.isoformat(timespec="seconds"),
            "expires_at": expires_at.isoformat(timespec="seconds"),
            "size": len(payload),
        }
        self._atomic_write(
            self._meta_path(key, namespace),
            json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8"),
        )

    def _read_payload_if_fresh(self, key: str, namespace: str = "") -> Optional[bytes]:
        meta = self._load_meta(key, namespace)
        if meta is None:
            return None
        if datetime.now() >= meta.expires_at:
            return None
        data_path = self._data_path(key, namespace)
        if not data_path.exists():
            return None
        return data_path.read_bytes()

    # ---------- 公共接口 ----------

    async def get(self, key: str, namespace: str = "") -> Optional[Any]:
        """命中且未过期返回反序列化后的值，否则返回 None。

        namespace: 缓存子目录（不同 provider 用不同 namespace 隔离）。
        """
        data = await asyncio.to_thread(self._read_payload_if_fresh, key, namespace)
        return None if data is None else self._decode(data)

    async def set(self, key: str, value: Any, *, ttl: CacheTTL, namespace: str = "") -> None:
        """序列化后原子写入；同时刷新 meta。

        namespace: 缓存子目录（不同 provider 用不同 namespace 隔离）。
        """
        await asyncio.to_thread(self._write_entry, key, self._encode(value), ttl, namespace)

    async def delete(self, key: str, namespace: str = "") -> bool:
        """删除该 key 的负载与 meta，返回是否实际删除了文件。"""

        def _do() -> bool:
            removed = False
            data_path = self._data_path(key, namespace)
            if data_path.exists():
                data_path.unlink()
                removed = True
            meta_path = self._meta_path(key, namespace)
            if meta_path.exists():
                meta_path.unlink()
                removed = True
            return removed

        return await asyncio.to_thread(_do)

    async def clear(self, prefix: str = "", namespace: str = "") -> int:
        """删除原始 key 以 prefix 开头、且属于本子类 content_type 的所有条目。

        namespace: 限定在某个子目录内清理（默认整个缓存目录）。
        """

        def _do() -> int:
            target_dir = self._dir_for(namespace)
            if not target_dir.exists():
                return 0
            count = 0
            suffix = f".{self._content_type}.meta.json"
            for meta_file in target_dir.glob(f"*{suffix}"):
                try:
                    raw = json.loads(meta_file.read_text(encoding="utf-8"))
                    if not raw.get("key", "").startswith(prefix):
                        continue
                    data_path = target_dir / (meta_file.name[: -len(".meta.json")])
                    if data_path.exists():
                        data_path.unlink()
                    meta_file.unlink()
                    count += 1
                except (json.JSONDecodeError, OSError):
                    continue
            return count

        return await asyncio.to_thread(_do)
