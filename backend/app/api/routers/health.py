from fastapi import APIRouter
from pydantic import BaseModel
import time

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    ok: bool
    ts_ms: int

class BrokerStatusResponse(BaseModel):
    connected: bool
    user_id_masked: str
    session_ok: bool
    last_refresh_ms: int
    message: str

@router.get("/health", response_model=HealthResponse)
async def get_health():
    return {"ok": True, "ts_ms": int(time.time() * 1000)}

@router.get("/broker/status", response_model=BrokerStatusResponse)
async def get_broker_status():
    # Mock response for Phase 4
    return {
        "connected": True,
        "user_id_masked": "AB***123",
        "session_ok": True,
        "last_refresh_ms": int(time.time() * 1000),
        "message": "Broker connected successfully"
    }
