import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# ...existing code...
from memcache_client import MemcacheClient

app = FastAPI(title="Memcached FastAPI Writer")

MEMCACHED_HOST = os.getenv("MEMCACHED_HOST", "127.0.0.1")
MEMCACHED_PORT = int(os.getenv("MEMCACHED_PORT", "11211"))

mc: Optional[MemcacheClient] = None


class SetRequest(BaseModel):
    key: str
    value: str
    expire: Optional[int] = 0


@app.on_event("startup")
def startup_event():
    global mc
    mc = MemcacheClient(host=MEMCACHED_HOST, port=MEMCACHED_PORT)


@app.on_event("shutdown")
def shutdown_event():
    global mc
    if mc:
        mc.close()
        mc = None


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


@app.get("/health")
def health():
    # simple health check
    return {"status": "ok", "memcached": f"{MEMCACHED_HOST}:{MEMCACHED_PORT}"}
