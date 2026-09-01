from fastapi import Request
from fastapi.responses import JSONResponse
from .models import ErrorBody
import logging

logger = logging.getLogger(__name__)

class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def app_error_handler(request: Request, exc: AppError):
    logger.warning(f"AppError: {exc.code} - {exc.message}")
    error_body = ErrorBody(code=exc.code, message=exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error_body.model_dump()}
    )
