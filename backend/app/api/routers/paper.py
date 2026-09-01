from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.core.engine.paper import PaperEngine

router = APIRouter()

class StartPaperRequest(BaseModel):
    strategy_name: str
    symbol: str
    resolution: str

@router.post("/paper/start")
async def start_paper(req: StartPaperRequest):
    session_id = f"{req.strategy_name}_{req.symbol}"
    if session_id in PaperEngine._instances and PaperEngine._instances[session_id].is_running:
        return {"success": False, "message": "Engine already running for this symbol/strategy."}
        
    engine = PaperEngine(session_id, req.strategy_name, req.symbol, req.resolution)
    PaperEngine._instances[session_id] = engine
    await engine.start()
    
    return {"success": True, "message": "Paper Engine streaming started in background."}

@router.post("/paper/stop")
async def stop_paper(req: StartPaperRequest):
    session_id = f"{req.strategy_name}_{req.symbol}"
    if session_id in PaperEngine._instances:
        PaperEngine._instances[session_id].stop()
        del PaperEngine._instances[session_id]
        return {"success": True, "message": "Paper Engine stopped."}
    return {"success": False, "message": "Engine not running."}

@router.get("/paper/portfolio")
async def get_portfolio(strategy_name: str, symbol: str):
    session_id = f"{strategy_name}_{symbol}"
    if session_id in PaperEngine._instances:
        return {"success": True, "data": PaperEngine._instances[session_id].get_portfolio(), "is_running": True}
    return {"success": True, "data": None, "is_running": False}
