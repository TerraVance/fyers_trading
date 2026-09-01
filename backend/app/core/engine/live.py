import asyncio
import time
import random
import pandas as pd
from typing import Dict, Any, Optional
from backend.app.infrastructure.data.cache import ParquetCache
from backend.app.core.engine.backtest import BacktestEngine
from backend.app.core.engine.risk_guard import RiskManager
from backend.app.infrastructure.broker.base import AbstractBroker, OrderIntent

class LiveEngine:
    _instances: Dict[str, 'LiveEngine'] = {}

    def __init__(self, session_id: str, strategy_name: str, symbol: str, resolution: str, broker: AbstractBroker):
        self.session_id = session_id
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.resolution = resolution
        self.broker = broker
        
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.tracker_task: Optional[asyncio.Task] = None
        
        self.cache = ParquetCache()
        temp_engine = BacktestEngine()
        StrategyClass = temp_engine._load_strategy(strategy_name)
        self.strategy_instance = StrategyClass()
        
        # Real Portfolio State
        try:
            self.real_cash = self.broker.get_funds()
        except Exception as e:
            print(f"Warning: Failed to fetch funds, using 0.0 - {e}")
            self.real_cash = 0.0
            
        self.positions = []
        self.orders = []
        
    async def start(self):
        self.is_running = True
        self.task = asyncio.create_task(self._run_loop())
        self.tracker_task = asyncio.create_task(self._order_tracker())
        
    def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
        if self.tracker_task:
            self.tracker_task.cancel()
            
    async def _order_tracker(self):
        """ Polls broker for order updates """
        while self.is_running:
            for order in self.orders:
                if order['status'] == 'PENDING':
                    try:
                        # Call Real Broker API
                        new_status = self.broker.get_order_status(order['broker_id'])
                        if new_status in ["FILLED", "REJECTED", "CANCELLED"]:
                            order['status'] = new_status
                            if new_status == "REJECTED":
                                order['reject_reason'] = "Broker Rejected Order (Check Margin or Auth)"
                                print(f"BROKER REJECTED ORDER {order['broker_id']}!")
                                RiskManager.kill()
                    except Exception as e:
                        print(f"Live Tracker Error polling {order['broker_id']}: {e}")
                        
            # Rate limit polling to max once every 2 seconds to respect Fyers API
            await asyncio.sleep(2)

    async def _run_loop(self):
        df = self.cache.load_data(self.symbol, self.resolution)
        if df.empty or len(df) < 500:
            print("Live Engine Error: Not enough data for warmup.")
            return
            
        start_idx = 500
        pending_action = None
        
        for i in range(start_idx, len(df)):
            if not self.is_running:
                break
                
            current_time = df.index[i]
            current_open = float(df.iloc[i]['open'])
            current_close = float(df.iloc[i]['close'])
            
            realized_pnl = 0.0
            has_position = len(self.positions) > 0
            
            # 1. Execute Pending Action at CURRENT OPEN (T+1 Execution)
            if pending_action == "BUY" and not has_position:
                intent_qty = self.real_cash / current_open
                can_execute, reason = RiskManager.can_trade(
                    current_cash=self.real_cash,
                    initial_capital=100000.0,
                    open_positions=self.positions,
                    realized_pnl=realized_pnl,
                    intent_qty=intent_qty,
                    intent_price=current_open
                )
                
                if can_execute:
                    intent = OrderIntent(
                        symbol=self.symbol, exchange="NSE", qty=int(intent_qty), 
                        side="BUY", order_type="MARKET", product="INTRADAY"
                    )
                    try:
                        broker_id = self.broker.place_order(intent)
                        self.real_cash -= (intent_qty * current_open)
                        self.positions.append({
                            "entry_time": current_time,
                            "entry_price": current_open,
                            "qty": intent_qty
                        })
                        self.orders.append({
                            "time": current_time,
                            "broker_id": broker_id,
                            "type": "BUY (MARKET)",
                            "price": current_open,
                            "qty": intent_qty,
                            "status": "PENDING",
                            "reject_reason": None
                        })
                    except Exception as e:
                        print(f"FAILED TO PLACE BUY ORDER: {e}")
                else:
                    print(f"Risk Guard Blocked LIVE Trade: {reason}")
                
            elif pending_action == "SELL" and has_position:
                pos = self.positions.pop()
                intent = OrderIntent(
                    symbol=self.symbol, exchange="NSE", qty=int(pos['qty']), 
                    side="SELL", order_type="MARKET", product="INTRADAY"
                )
                try:
                    broker_id = self.broker.place_order(intent)
                    exit_revenue = pos['qty'] * current_open
                    self.real_cash += exit_revenue
                    
                    self.orders.append({
                        "time": current_time,
                        "broker_id": broker_id,
                        "type": "SELL (MARKET)",
                        "price": current_open,
                        "qty": pos['qty'],
                        "status": "PENDING",
                        "reject_reason": None
                    })
                except Exception as e:
                    print(f"FAILED TO PLACE SELL ORDER: {e}")
                    # Push position back if failed
                    self.positions.append(pos)
                
            # Memory Leak Prevention: Cap orders history at 1000
            if len(self.orders) > 1000:
                self.orders.pop(0)
                
            # 2. Evaluate Strategy at CURRENT CLOSE for the NEXT candle
            buffer_df = df.iloc[i-499 : i+1].copy()
            signal_df = self.strategy_instance.generate_signals(buffer_df)
            pending_action = signal_df.iloc[-1].get('signal')
                
            if RiskManager.is_killed() and len(self.positions) > 0:
                print("Kill Switch Active! Liquidating all live positions...")
                while len(self.positions) > 0:
                    pos = self.positions.pop()
                    intent = OrderIntent(
                        symbol=self.symbol, exchange="NSE", qty=int(pos['qty']), 
                        side="SELL", order_type="MARKET", product="INTRADAY"
                    )
                    try:
                        broker_id = self.broker.place_order(intent)
                        exit_revenue = pos['qty'] * current_open
                        self.real_cash += exit_revenue
                        self.orders.append({
                            "time": current_time,
                            "broker_id": broker_id,
                            "type": "LIQUIDATE (MARKET)",
                            "price": current_open,
                            "qty": pos['qty'],
                            "status": "PENDING",
                            "reject_reason": None
                        })
                    except Exception as e:
                        print(f"Kill Switch Failed to Liquidate! {e}")
                
            # Wait 2 seconds to simulate slower live market
            await asyncio.sleep(2)

    def get_portfolio(self):
        return {
            "current_cash": round(self.real_cash, 2),
            "open_positions": self.positions,
            "orders": list(reversed(self.orders[-20:]))
        }
