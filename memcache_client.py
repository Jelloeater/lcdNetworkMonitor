from pymemcache.client.base import Client as PymemcacheClient
from typing import Optional


class MemcacheClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 11211):
        # ...existing code...
        self.host = host
        self.port = port
        self.client = PymemcacheClient((host, port), connect_timeout=1, timeout=1)

    def set(self, key: str, value: str, expire: int = 0) -> bool:
        # value stored as bytes/str; pymemcache handles encoding
        return self.client.set(key, value, expire=expire)

    def get(self, key: str) -> Optional[str]:
        raw = self.client.get(key)
        if raw is None:
            return None
        if isinstance(raw, bytes):
            try:
                return raw.decode("utf-8")
            except Exception:
                return raw.decode("latin-1", errors="ignore")
        return str(raw)

    def close(self):
        try:
            self.client.close()
        except Exception:
            pass
