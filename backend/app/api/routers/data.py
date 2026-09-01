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
        return {"success": True, "message": f"Successfully cached data for {req.symbol}", "rows_downloaded": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
