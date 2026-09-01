from typing import Dict, Any, List, Tuple

class RiskConfig:
    MAX_DAILY_LOSS = -5000.0  # Max loss in base currency (INR)
    MAX_OPEN_POSITIONS = 3    # Maximum simultaneous open positions
    MAX_POSITION_SIZE_PCT = 1.0 # Max capital % per trade (100%)

class RiskManager:
    _is_killed = False

    @classmethod
    def kill(cls):
        cls._is_killed = True
        print("CRITICAL: GLOBAL KILL SWITCH ACTIVATED!")

    @classmethod
    def reset(cls):
        cls._is_killed = False
        print("Risk Guard Reset. Systems Online.")

    @classmethod
    def is_killed(cls) -> bool:
        return cls._is_killed

    @classmethod
    def can_trade(cls, current_cash: float, initial_capital: float, open_positions: List[Dict], realized_pnl: float, intent_qty: float, intent_price: float) -> Tuple[bool, str]:
        if cls._is_killed:
            return False, "Global Kill Switch is ACTIVE."

        if realized_pnl <= RiskConfig.MAX_DAILY_LOSS:
            cls.kill() # Auto-trip the kill switch if we bleed too much
            return False, f"Max Daily Loss exceeded: {realized_pnl}"

        if len(open_positions) >= RiskConfig.MAX_OPEN_POSITIONS:
            return False, f"Max Open Positions reached: {RiskConfig.MAX_OPEN_POSITIONS}"

        trade_cost = intent_qty * intent_price
        max_cost = initial_capital * RiskConfig.MAX_POSITION_SIZE_PCT
        if trade_cost > max_cost:
            return False, f"Trade cost {trade_cost} exceeds max position size {max_cost}"
            
        if trade_cost > current_cash:
            return False, f"Insufficient funds: Have {current_cash}, need {trade_cost}"

        return True, "OK"
