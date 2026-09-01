from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.core.engine.live import LiveEngine
from backend.app.api.routers.broker import fyers_broker

router = APIRouter()

class StartLiveRequest(BaseModel):
    strategy_name: str
    symbol: str
    resolution: str

@router.post("/live/start")
async def start_live(req: StartLiveRequest):
    session_id = f"{req.strategy_name}_{req.symbol}"
    if session_id in LiveEngine._instances and LiveEngine._instances[session_id].is_running:
        return {"success": False, "message": "Live Engine already running for this symbol."}
        
    try:
        engine = LiveEngine(session_id, req.strategy_name, req.symbol, req.resolution, broker=fyers_broker)
        LiveEngine._instances[session_id] = engine
        await engine.start()
        return {"success": True, "message": "LIVE TRADING COMMENCED. Broker connections active."}
    except Exception as e:
        return {"success": False, "message": f"Failed to start live engine: {str(e)}"}

@router.post("/live/stop")
async def stop_live(req: StartLiveRequest):
    session_id = f"{req.strategy_name}_{req.symbol}"
    if session_id in LiveEngine._instances:
        LiveEngine._instances[session_id].stop()
        del LiveEngine._instances[session_id]
        return {"success": True, "message": "Live Engine halted gracefully."}
    return {"success": False, "message": "Engine not running."}

@router.get("/live/portfolio")
async def get_portfolio(strategy_name: str, symbol: str):
    session_id = f"{strategy_name}_{symbol}"
    if session_id in LiveEngine._instances:
        return {"success": True, "data": LiveEngine._instances[session_id].get_portfolio(), "is_running": True}
    return {"success": True, "data": None, "is_running": False}

@router.get("/live/sessions/active")
async def active_sessions():
    return {"sessions": list(LiveEngine._instances.keys())}

@router.get("/live/orders")
async def get_orders():
    # Helper endpoint to match previous stub, handled directly in portfolio now
    return {"orders": []}
