import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
from memcache_client import MemcacheClient
import uvicorn
from contextlib import asynccontextmanager
import argparse

MEMCACHED_HOST = os.getenv("MEMCACHED_HOST", "127.0.0.1")
MEMCACHED_PORT = int(os.getenv("MEMCACHED_PORT", "11211"))
VALKEY_HOST = os.getenv("VALKEY_HOST", "127.0.0.1")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", "12345"))

class ValkeyClient:
    """Stub Valkey client."""
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.storage = {}

    def set(self, key: str, value: str, expire: int = 0) -> bool:
        # NOTE: The 'expire' parameter is ignored in this stub implementation.
        self.storage[key] = value
        return True

    def get(self, key: str) -> Optional[str]:
        return self.storage.get(key)

    def close(self):
        pass

class Backend:
    def __init__(self, use_valkey=False):
        if use_valkey:
            self.client = ValkeyClient(host=VALKEY_HOST, port=VALKEY_PORT)
        else:
            self.client = MemcacheClient(host=MEMCACHED_HOST, port=MEMCACHED_PORT)

    def set(self, key: str, value: str, expire: int = 0) -> bool:
        return self.client.set(key, value, expire)

    def get(self, key: str) -> Optional[str]:
        return self.client.get(key)

    def close(self):
        self.client.close()

backend: Optional[Backend] = None

@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager: initialize backend on startup and close on shutdown."""
    global backend
    use_valkey = os.getenv("USE_VALKEY", "false").lower() in ("1", "true", "yes")
    backend = Backend(use_valkey=use_valkey)
    try:
        yield
    finally:
        if backend:
            backend.close()
            backend = None

app = FastAPI(title="Flexible Backend FastAPI", lifespan=lifespan)

class SetRequest(BaseModel):
    key: str
    value: str
    expire: Optional[int] = 0

@app.post("/set")
def set_value(req: SetRequest):
    global backend
    if backend is None:
        raise HTTPException(status_code=500, detail="Backend not initialized")
    try:
        ok = backend.set(req.key, req.value, expire=req.expire or 0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend set error: {e}")
    return {"stored": bool(ok)}

@app.get("/get/{key}")
def get_value(key: str):
    global backend
    if backend is None:
        raise HTTPException(status_code=500, detail="Backend not initialized")
    try:
        val = backend.get(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend get error: {e}")
    if val is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": val}

@app.get("/health")
def health():
    return {"status": "ok", "backend": "valkey" if os.getenv("USE_VALKEY", "false").lower() in ("1", "true", "yes") else "memcache"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastAPI backend web server")
    parser.add_argument(
        "--host", default=os.getenv("HOST", "0.0.0.0"), help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Port to bind to",
    )
    parser.add_argument(
        "--log-level", default=os.getenv("LOG_LEVEL", "info"), help="Uvicorn log level"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload (development)"
    )
    args = parser.parse_args()

    host = args.host
    port = args.port
    log_level = args.log_level
    reload = args.reload or (
        os.getenv("RELOAD", "false").lower() in ("1", "true", "yes")
    )

    uvicorn.run(app, host=host, port=port, log_level=log_level, reload=reload)
