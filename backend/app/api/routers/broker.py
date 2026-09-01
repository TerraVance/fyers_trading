from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.infrastructure.broker.fyers import FyersBroker

router = APIRouter(tags=["broker"])

# We instantiate the broker globally for the API to access, usually this goes in a dependency injection container.
fyers_broker = FyersBroker(
    client_id=settings.fyers_app_id,
    secret_key=settings.fyers_secret_key,
    redirect_uri=settings.fyers_redirect_uri
)

class AuthCodeRequest(BaseModel):
    auth_code: str

class BrokerLoginResponse(BaseModel):
    login_url: str

class BrokerAuthResponse(BaseModel):
    success: bool
    message: str

@router.get("/broker/login_url", response_model=BrokerLoginResponse)
async def get_broker_login_url():
    """Generates the URL the user must click to login to Fyers."""
    try:
        url = fyers_broker.get_login_url()
        return {"login_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broker/submit_auth", response_model=BrokerAuthResponse)
async def submit_broker_auth(req: AuthCodeRequest):
    """Takes the URL the user copied after logging in, extracts the auth code, and generates the access token."""
    success = fyers_broker.generate_token_from_url(req.auth_code)
    if success:
        return {"success": True, "message": "Successfully authenticated with Fyers"}
    return {"success": False, "message": "Failed to authenticate. Ensure the URL is correct and not expired."}
