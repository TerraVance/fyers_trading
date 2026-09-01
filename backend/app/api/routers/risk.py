from fastapi import APIRouter
from backend.app.core.engine.risk_guard import RiskManager

router = APIRouter()

@router.post("/risk/kill")
async def trigger_kill_switch():
    RiskManager.kill()
    return {"success": True, "message": "Global Kill Switch Engaged. All engines blocked and liquidating."}

@router.post("/risk/reset")
async def reset_kill_switch():
    RiskManager.reset()
    return {"success": True, "message": "Risk Guard Reset. Systems Online."}
    
@router.get("/risk/status")
async def get_risk_status():
    return {"success": True, "is_killed": RiskManager.is_killed()}
