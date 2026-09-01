from typing import List, Dict, Any, Optional
import time
from .base import AbstractBroker, OrderIntent

class FakeBroker(AbstractBroker):
    def __init__(self):
        self.orders = {}
        self.order_counter = 1000

    def get_login_url(self) -> str:
        return "http://fake-broker.local/login"

    def generate_token_from_url(self, redirected_url: str) -> bool:
        return True

    def get_historical_candles(self, symbol: str, resolution: str, start_epoch: int, end_epoch: int) -> List[Dict[str, Any]]:
        return [] # Return empty for mock

    def place_order(self, intent: OrderIntent) -> str:
        order_id = f"FAKE_{self.order_counter}"
        self.order_counter += 1
        
        self.orders[order_id] = {
            "id": order_id,
            "symbol": intent.symbol,
            "qty": intent.qty,
            "side": intent.side,
            "status": "FILLED" # instantly fill in fake broker
        }
        return order_id

    def get_order_status(self, broker_order_id: str) -> str:
        if broker_order_id in self.orders:
            return self.orders[broker_order_id]["status"]
        return "UNKNOWN"

    def get_positions(self) -> List[Dict[str, Any]]:
        return []

    def get_funds(self) -> float:
        return 100000.0
