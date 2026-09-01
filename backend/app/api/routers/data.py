from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from backend.app.infrastructure.data.downloader import DataDownloader
from backend.app.api.routers.broker import fyers_broker

router = APIRouter(tags=["data"])
downloader = DataDownloader(fyers_broker)

class DownloadRequest(BaseModel):
    symbol: str
    resolution: str
    start_ms: int
    end_ms: int

class DownloadResponse(BaseModel):
    success: bool
    message: str
    rows_downloaded: int
    actual_start_ms: int = 0
    actual_end_ms: int = 0

@router.post("/data/download", response_model=DownloadResponse)
async def download_historical_data(req: DownloadRequest):
    """
    Triggers the downloader engine. Wrapped in to_thread to prevent blocking the event loop.
    """
    try:
        df = await asyncio.to_thread(
            downloader.download_history, 
            req.symbol, 
            req.resolution, 
            req.start_ms, 
            req.end_ms
        )
        
        actual_start = 0
        actual_end = 0
        if not df.empty and 'time' in df.columns:
            actual_start = int(df['time'].iloc[0].timestamp() * 1000)
            actual_end = int(df['time'].iloc[-1].timestamp() * 1000)

        return {
            "success": True, 
            "message": f"Successfully cached data for {req.symbol}", 
            "rows_downloaded": len(df),
            "actual_start_ms": actual_start,
            "actual_end_ms": actual_end
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from backend.app.infrastructure.data.symbol_master import symbol_master

@router.get("/data/symbols")
async def search_symbols(query: str = ""):
    try:
        # First query might block while downloading CSVs, so wrap in to_thread
        results = await asyncio.to_thread(symbol_master.search, query)
        return {"success": True, "items": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
