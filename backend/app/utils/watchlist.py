import yaml
from pathlib import Path
from backend.app.core.errors import AppError
from pydantic import BaseModel
from typing import List

class WatchlistItem(BaseModel):
    symbol: str
    exchange: str
    token: str
    trading_symbol: str
    sync_1m: bool = False
    sync_daily: bool = False
    live: bool = False

class Watchlist(BaseModel):
    items: List[WatchlistItem]

def load_watchlist(filepath: str = "config/watchlist.yaml") -> Watchlist:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return Watchlist(**data)
