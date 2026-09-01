from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    aliceblue_user_id: Optional[str] = None
    aliceblue_api_key: Optional[str] = None
    live_armed: bool = False
    max_notional_per_order: float = 100000.0
    max_qty_per_order: int = 1000
    database_url: str = "postgresql://admin:secretpassword@localhost:5433/consistent"
    log_level: str = "INFO"
    environment: str = "development"
    
    # Fyers API config
    fyers_app_id: str = "YOUR_APP_ID"
    fyers_secret_key: str = "YOUR_SECRET_KEY"
    fyers_redirect_uri: str = "http://localhost:8000/api/v1/broker/callback"
    
    # OpenAI API config
    openai_api_key: str = "sk-..."

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Global singleton
settings = Settings()
