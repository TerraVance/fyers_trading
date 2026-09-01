import asyncio
import time
import pandas as pd
from typing import Dict, Any, Optional
from backend.app.infrastructure.data.cache import ParquetCache
from backend.app.core.engine.backtest import BacktestEngine
from backend.app.core.engine.risk_guard import RiskManager

class PaperEngine:
    _instances: Dict[str, 'PaperEngine'] = {}

    def __init__(self, session_id: str, strategy_name: str, symbol: str, resolution: str, initial_capital: float = 10000.0):
        self.session_id = session_id
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.resolution = resolution
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
        # Load Strategy
        self.cache = ParquetCache()
        temp_engine = BacktestEngine()
        StrategyClass = temp_engine._load_strategy(strategy_name)
        self.strategy_instance = StrategyClass()
        
        self.positions = []
        self.trades = []
        
    async def start(self):
        self.is_running = True
        self.task = asyncio.create_task(self._run_loop())
        
    def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            
    async def _run_loop(self):
        # SIMULATION OF LIVE FEED
        # To avoid making actual Fyers API calls in Paper Mode right now,
        # we stream the parquet data 1 row per second to simulate the live tick.
        
        df = self.cache.load_data(self.symbol, self.resolution)
        if df.empty or len(df) < 500:
            print("Paper Engine Error: Not enough data for warmup.")
            return
            
        start_idx = 500
        pending_action = None
        
        for i in range(start_idx, len(df)):
            if not self.is_running:
                break
                
            current_time = df.index[i]
            current_open = float(df.iloc[i]['open'])
            current_close = float(df.iloc[i]['close'])
            
            # Calculate current realized PNL
            realized_pnl = sum([t['pnl'] for t in self.trades if t.get('pnl') is not None])
            has_position = len(self.positions) > 0
            
            # 1. Execute Pending Action at CURRENT OPEN (T+1 Execution)
            if pending_action == "BUY" and not has_position:
                intent_qty = self.current_cash / current_open
                can_execute, reason = RiskManager.can_trade(
                    current_cash=self.current_cash,
                    initial_capital=self.initial_capital,
                    open_positions=self.positions,
                    realized_pnl=realized_pnl,
                    intent_qty=intent_qty,
                    intent_price=current_open
                )
                
                if can_execute:
                    self.current_cash -= (intent_qty * current_open)
                    self.positions.append({
                        "entry_time": current_time,
                        "entry_price": current_open,
                        "qty": intent_qty
                    })
                    self.trades.append({
                        "time": current_time,
                        "type": "BUY",
                        "price": current_open,
                        "qty": intent_qty,
                        "pnl": 0.0
                    })
                else:
                    print(f"Risk Guard Blocked Trade: {reason}")
                
            elif pending_action == "SELL" and has_position:
                # We always allow liquidating (selling) to reduce risk
                pos = self.positions.pop()
                exit_revenue = pos['qty'] * current_open
                self.current_cash += exit_revenue
                
                self.trades.append({
                    "time": current_time,
                    "type": "SELL",
                    "price": current_open,
                    "qty": pos['qty'],
                    "pnl": exit_revenue - (pos['qty'] * pos['entry_price'])
                })
                
            # Memory Leak Prevention: Cap trades history at 1000
            if len(self.trades) > 1000:
                self.trades.pop(0)
                
            # 2. Evaluate Strategy at CURRENT CLOSE for the NEXT candle
            buffer_df = df.iloc[i-499 : i+1].copy()
            signal_df = self.strategy_instance.generate_signals(buffer_df)
            pending_action = signal_df.iloc[-1].get('signal')
                
            # If Kill Switch is hit and we have positions, liquidate immediately
            if RiskManager.is_killed() and len(self.positions) > 0:
                print("Kill Switch Active! Liquidating all positions...")
                while len(self.positions) > 0:
                    pos = self.positions.pop()
                    exit_revenue = pos['qty'] * current_close
                    self.current_cash += exit_revenue
                    self.trades.append({
                        "time": current_time,
                        "type": "LIQUIDATE (KILL SWITCH)",
                        "price": current_close,
                        "qty": pos['qty'],
                        "pnl": exit_revenue - (pos['qty'] * pos['entry_price'])
                    })
                
            # Wait 1 second to simulate time passing (streaming speed)
            await asyncio.sleep(1)

    def get_portfolio(self):
        return {
            "initial_capital": self.initial_capital,
            "current_cash": round(self.current_cash, 2),
            "open_positions": self.positions,
            "trades": list(reversed(self.trades[-20:]))
        }
