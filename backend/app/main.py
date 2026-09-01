from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.errors import AppError
from backend.app.utils.logger import setup_logging
import logging

from backend.app.api.routers import health, config, backtests, live, broker, data, strategy, paper, risk
from backend.app.api.ws.manager import manager

logger = logging.getLogger(__name__)

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )

def create_app() -> FastAPI:
    setup_logging()
    
    app = FastAPI(title="Consistent Trading Platform")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # For local development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_exception_handler(AppError, app_error_handler)
    
    # Register Routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(config.router, prefix="/api/v1")
    app.include_router(backtests.router, prefix="/api/v1")
    app.include_router(live.router, prefix="/api/v1")
    app.include_router(broker.router, prefix="/api/v1")
    app.include_router(data.router, prefix="/api/v1")
    app.include_router(strategy.router, prefix="/api/v1")
    app.include_router(paper.router, prefix="/api/v1")
    app.include_router(risk.router, prefix="/api/v1")

    @app.websocket("/ws/v1/stream")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                # Keep connection alive, wait for client messages if any
                data = await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            
    return app

app = create_app()
