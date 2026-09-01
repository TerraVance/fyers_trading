import os
from typing import List, Dict, Any, Optional
from fyers_apiv3 import fyersModel
from .base import AbstractBroker, OrderIntent

class FyersBroker(AbstractBroker):
    def __init__(self, client_id: str, secret_key: str, redirect_uri: str):
        self.client_id = client_id
        self.secret_key = secret_key
        self.redirect_uri = redirect_uri
        self.session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key,
            redirect_uri=self.redirect_uri,
            response_type="code",
            grant_type="authorization_code"
        )
        self.fyers = None

    def get_login_url(self) -> str:
        return self.session.generate_authcode()

    def generate_token_from_url(self, redirected_url: str) -> bool:
        # The user pastes the full redirected URL or just the auth code
        try:
            if "auth_code=" in redirected_url:
                auth_code = redirected_url.split("auth_code=")[1].split("&")[0]
            else:
                auth_code = redirected_url

            self.session.set_token(auth_code)
            response = self.session.generate_token()
            if "access_token" in response:
                access_token = response["access_token"]
                self.fyers = fyersModel.FyersModel(
                    client_id=self.client_id,
                    is_async=False,
                    token=access_token,
                    log_path=""
                )
                return True
            return False
        except Exception as e:
            print(f"Error generating token: {e}")
            return False

    def get_historical_candles(self, symbol: str, resolution: str, start_epoch: int, end_epoch: int) -> List[Dict[str, Any]]:
        if not self.fyers:
            raise Exception("Broker not authenticated")
            
        data = {
            "symbol": symbol,
            "resolution": resolution,
            "date_format": "0",
            "range_from": str(start_epoch),
            "range_to": str(end_epoch),
            "cont_flag": "1"
        }
        res = self.fyers.history(data=data)
        if res.get("s") == "ok":
            candles = []
            for c in res["candles"]:
                candles.append({
                    "time": int(c[0] * 1000), # convert s to ms
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": int(c[5])
                })
            return candles
        return []

    def place_order(self, intent: OrderIntent) -> str:
        if not self.fyers:
            raise Exception("Broker not authenticated")
            
        data = {
            "symbol": intent.symbol,
            "qty": intent.qty,
            "type": 2 if intent.order_type == "MARKET" else 1,
            "side": 1 if intent.side == "BUY" else -1,
            "productType": intent.product,
            "limitPrice": intent.limit_price or 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
        }
        res = self.fyers.place_order(data=data)
        if res.get("s") == "ok":
            return res.get("id")
        raise Exception(f"Failed to place order: {res}")

    def get_order_status(self, broker_order_id: str) -> str:
        if not self.fyers:
            raise Exception("Broker not authenticated")
        res = self.fyers.orderbook()
        if res.get("s") == "ok":
            for order in res["orderBook"]:
                if order["id"] == broker_order_id:
                    status_id = order["status"]
                    if status_id == 2: return "FILLED"
                    if status_id == 5: return "REJECTED"
                    if status_id == 6: return "CANCELLED"
                    return "OPEN"
        return "UNKNOWN"

    def get_positions(self) -> List[Dict[str, Any]]:
        if not self.fyers:
            raise Exception("Broker not authenticated")
        res = self.fyers.positions()
        if res.get("s") == "ok":
            return res.get("netPositions", [])
        return []

    def get_funds(self) -> float:
        if not self.fyers:
            raise Exception("Broker not authenticated")
        res = self.fyers.funds()
        if res.get("s") == "ok":
            for fund in res.get("fund_limit", []):
                if fund.get("title") == "Available Balance":
                    return float(fund.get("equityAmount", 0.0))
        return 0.0
