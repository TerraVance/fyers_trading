from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from typing import Any, Dict, List, Optional
from backend.app.core.engine.backtest import BacktestEngine

router = APIRouter(tags=["backtest"])
engine = BacktestEngine(initial_capital=10000.0)

class BacktestRequest(BaseModel):
    strategy_name: str
    symbol: str
    resolution: str
    start_ms: int
    end_ms: int

class BacktestResponse(BaseModel):
    success: bool
    metrics: Optional[Dict[str, Any]] = None
    chart_data: Optional[List[Dict[str, Any]]] = None
    execution_log: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

@router.post("/backtest/run", response_model=BacktestResponse)
async def run_backtest(req: BacktestRequest):
    """
    Runs the Backtest engine asynchronously to avoid blocking the API.
    """
    try:
        result = await asyncio.to_thread(
            engine.run,
            req.strategy_name,
            req.symbol,
            req.resolution,
            req.start_ms,
            req.end_ms
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
            
        return {
            "success": True, 
            "metrics": result["metrics"],
            "chart_data": result.get("chart_data", []),
            "execution_log": result.get("execution_log", [])
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
