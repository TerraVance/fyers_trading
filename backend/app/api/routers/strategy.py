from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from backend.app.core.strategy.generator import StrategyGenerator

router = APIRouter(tags=["strategy"])
generator = StrategyGenerator()

class GenerateRequest(BaseModel):
    strategy_name: str
    description: str

class GenerateResponse(BaseModel):
    success: bool
    message: str
    file_path: str

@router.post("/strategy/generate", response_model=GenerateResponse)
async def generate_strategy(req: GenerateRequest):
    """
    Triggers the LLM Strategy Generator. Wrapped in to_thread since LLM calls are blocking.
    """
    try:
        code = await asyncio.to_thread(
            generator.generate_strategy_code, 
            req.strategy_name, 
            req.description
        )
        filepath = generator.save_strategy(req.strategy_name, code)
        return {"success": True, "message": f"Successfully generated {req.strategy_name}", "file_path": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
