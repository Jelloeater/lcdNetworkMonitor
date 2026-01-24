import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from memcache_client import MemcacheClient
import uvicorn
from contextlib import asynccontextmanager
import argparse

MEMCACHED_HOST = os.getenv("MEMCACHED_HOST", "127.0.0.1")
MEMCACHED_PORT = int(os.getenv("MEMCACHED_PORT", "11211"))

mc: Optional[MemcacheClient] = None


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager: initialize memcache client on startup and close on shutdown."""
    global mc
    mc = MemcacheClient(host=MEMCACHED_HOST, port=MEMCACHED_PORT)
    try:
        yield
    finally:
        if mc:
            mc.close()
            mc = None


app = FastAPI(title="Memcached FastAPI Writer", lifespan=lifespan)


class SetRequest(BaseModel):
    key: str
    value: str
    expire: Optional[int] = 0


@app.post("/set")
def set_value(req: SetRequest):
    global mc
    if mc is None:
        raise HTTPException(status_code=500, detail="Memcache client not initialized")
    try:
        ok = mc.set(req.key, req.value, expire=req.expire or 0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memcache set error: {e}")
    return {"stored": bool(ok)}


@app.get("/get/{key}")
def get_value(key: str):
    global mc
    if mc is None:
        raise HTTPException(status_code=500, detail="Memcache client not initialized")
    try:
        val = mc.get(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memcache get error: {e}")
    if val is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": val}


@app.get("/status/{req}")
def set_screen(req: str):
    global mc
    if mc is None:
        raise HTTPException(status_code=500, detail="Memcache client not initialized")
    try:
        return mc.set(key="status", value=req, expire=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memcache get error: {e}")


@app.get("/clear")
def clear_screen():
    global mc
    if mc is None:
        raise HTTPException(status_code=500, detail="Memcache client not initialized")
    try:
        return mc.set(key="status", value=(" " * 16), expire=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memcache get error: {e}")


@app.get("/health")
def health():
    # simple health check
    return {"status": "ok", "memcached": f"{MEMCACHED_HOST}:{MEMCACHED_PORT}"}


if __name__ == "__main__":
    # Run the FastAPI app with uvicorn when executed as a script.
    # Host, port, log level, and reload flag are configurable via environment variables
    # and via CLI flags (CLI overrides env vars).

    parser = argparse.ArgumentParser(description="Run the FastAPI memcache web server")
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
