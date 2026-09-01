from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class OrderIntent(BaseModel):
    symbol: str # e.g., INFY-EQ
    exchange: str # e.g., NSE
    qty: int
    side: str # "BUY" or "SELL"
    order_type: str # "MARKET" or "LIMIT"
    product: str # "CNC" or "INTRADAY"
    limit_price: Optional[float] = None

class AbstractBroker(ABC):
    
    @abstractmethod
    def get_login_url(self) -> str:
        """Return the URL the user needs to visit to login."""
        pass

    @abstractmethod
    def generate_token_from_url(self, redirected_url: str) -> bool:
        """Parses the auth_code from the URL and exchanges it for an access_token."""
        pass

    @abstractmethod
    def get_historical_candles(self, symbol: str, resolution: str, start_epoch: int, end_epoch: int) -> List[Dict[str, Any]]:
        """
        Fetch historical OHLCV data. 
        Returns list of dicts: [{'time': ms, 'open': float, 'high': float, 'low': float, 'close': float, 'volume': int}]
        """
        pass

    @abstractmethod
    def place_order(self, intent: OrderIntent) -> str:
        """Places an order and returns the broker's order ID."""
        pass

    @abstractmethod
    def get_order_status(self, broker_order_id: str) -> str:
        """Returns the status of the order (e.g., 'FILLED', 'REJECTED')."""
        pass
        
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Returns current open positions."""
        pass
        
    @abstractmethod
    def get_funds(self) -> float:
        """Returns available margin for trading."""
        pass
