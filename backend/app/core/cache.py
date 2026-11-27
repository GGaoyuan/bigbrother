"""容量有限且线程安全的过期缓存。"""

from collections import OrderedDict
from threading import Lock
from time import monotonic


class ExpiringCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.entries = OrderedDict()
        self.lock = Lock()

    def get(self, key):
        with self.lock:
            entry = self.entries.get(key)
            if entry is None:
                return None
            expiry, value = entry
            if expiry <= monotonic():
                del self.entries[key]
                return None
            self.entries.move_to_end(key)
            return value

    def put(self, key, value, ttl):
        with self.lock:
            self.entries[key] = (monotonic() + ttl, value)
            self.entries.move_to_end(key)
            if len(self.entries) > self.capacity:
                self.entries.popitem(last=False)
