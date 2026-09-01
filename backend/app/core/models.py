from pydantic import BaseModel
from typing import Optional, List

class Bar(BaseModel):
    symbol: str
    resolution: str
    ts_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: int

class Position(BaseModel):
    symbol: str
    qty: int
    total_cost: float
    side: str  # LONG, SHORT, FLAT

    @property
    def avg_price(self) -> float:
        return self.total_cost / self.qty if self.qty > 0 else 0.0

class StrategyContext(BaseModel):
    position: Optional[Position] = None
    orders_today: int = 0
    ltp: float = 0.0
    session_pnl: float = 0.0

class Signal(BaseModel):
    action: str  # BUY, SELL, EXIT, HOLD
    reason: str
    confidence: float = 1.0
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    trailing_stop_pct: Optional[float] = None

class OrderIntent(BaseModel):
    mode: str
    symbol: str
    exchange: str
    trading_symbol: str
    token: str
    side: str
    product: str
    order_type: str
    qty: int
    limit_price: Optional[float] = None

class Order(BaseModel):
    id: Optional[int] = None
    mode: str
    session_id: Optional[int] = None
    placed_at_ms: int
    updated_at_ms: int
    strategy_name: str
    symbol: str
    exchange: str
    trading_symbol: str
    token: str
    side: str
    product: str
    order_type: str
    qty: int
    limit_price: Optional[float] = None
    status: str
    avg_fill_price: Optional[float] = None
    filled_qty: int = 0
    broker_order_id: Optional[str] = None
    reject_reason: Optional[str] = None
    signal_reason: str
    realized_pnl: Optional[float] = None
    fees: float = 0.0

class BacktestRun(BaseModel):
    id: Optional[int] = None
    created_at_ms: int
    strategy_name: str
    strategy_version: str
    params_json: str
    symbol: str
    exchange: str
    resolution: str
    from_ms: int
    to_ms: int
    starting_capital: float
    brokerage_bps: float
    slippage_bps: float
    fill_rule: str
    status: str
    error: Optional[str] = None
    net_pnl: float
    return_pct: float
    ending_equity: float
    max_drawdown_pct: float
    n_trades: int
    n_wins: int
    n_losses: int
    win_rate: float
    fees_paid: float
    trades_json: str

class LiveSession(BaseModel):
    id: Optional[int] = None
    mode: str
    strategy_name: str
    strategy_version: str
    params_json: str
    symbols_json: str
    product: str
    started_at_ms: int
    last_active_ms: int
    stopped_at_ms: Optional[int] = None
    status: str
    state_file: str
    crash_reason: Optional[str] = None

class ErrorBody(BaseModel):
    code: str
    message: str
