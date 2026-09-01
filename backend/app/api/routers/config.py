from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(tags=["config"])

class WatchlistResponse(BaseModel):
    items: List[Dict[str, Any]]

class StrategyConfigResponse(BaseModel):
    items: List[Dict[str, Any]]

@router.get("/config/watchlist", response_model=WatchlistResponse)
async def get_watchlist():
    # Mock response representing what will eventually be parsed from yaml
    return {
        "items": [
            {
                "symbol": "INFY",
                "exchange": "NSE",
                "token": "1594",
                "trading_symbol": "INFY-EQ",
                "sync_1m": True,
                "sync_daily": True,
                "live": True
            }
        ]
    }

@router.get("/config/strategies", response_model=StrategyConfigResponse)
async def get_strategies():
    # Mock response
    return {
        "items": [
            {
                "name": "sma_momentum",
                "version": "1.0",
                "default_params": {
                    "fast_sma": 10,
                    "slow_sma": 50,
                    "rsi_filter": True
                }
            }
        ]
    }
