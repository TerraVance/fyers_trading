from sqlalchemy import Column, Integer, String, BigInteger, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .session import Base

class LiveSessionModel(Base):
    __tablename__ = "live_sessions"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String, nullable=False)
    strategy_name = Column(String, nullable=False)
    strategy_version = Column(String, nullable=False)
    params_json = Column(JSON, nullable=False)
    symbols_json = Column(JSON, nullable=False)
    product = Column(String, nullable=False)
    started_at_ms = Column(BigInteger, nullable=False)
    last_active_ms = Column(BigInteger, nullable=False)
    stopped_at_ms = Column(BigInteger, nullable=True)
    status = Column(String, nullable=False)
    state_file = Column(String, nullable=False)
    crash_reason = Column(String, nullable=True)

    orders = relationship("OrderModel", back_populates="session")


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String, nullable=False)
    session_id = Column(Integer, ForeignKey("live_sessions.id"), nullable=True)
    placed_at_ms = Column(BigInteger, nullable=False)
    updated_at_ms = Column(BigInteger, nullable=False)
    strategy_name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    trading_symbol = Column(String, nullable=False)
    token = Column(String, nullable=False)
    side = Column(String, nullable=False)
    product = Column(String, nullable=False)
    order_type = Column(String, nullable=False)
    qty = Column(Integer, nullable=False)
    limit_price = Column(Numeric, nullable=True)
    status = Column(String, nullable=False)
    avg_fill_price = Column(Numeric, nullable=True)
    filled_qty = Column(Integer, default=0, nullable=False)
    broker_order_id = Column(String, nullable=True)
    reject_reason = Column(String, nullable=True)
    signal_reason = Column(String, nullable=False)
    realized_pnl = Column(Numeric, nullable=True)
    fees = Column(Numeric, default=0.0, nullable=False)

    session = relationship("LiveSessionModel", back_populates="orders")


class BacktestRunModel(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at_ms = Column(BigInteger, nullable=False)
    strategy_name = Column(String, nullable=False)
    strategy_version = Column(String, nullable=False)
    params_json = Column(JSON, nullable=False)
    symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    resolution = Column(String, nullable=False)
    from_ms = Column(BigInteger, nullable=False)
    to_ms = Column(BigInteger, nullable=False)
    starting_capital = Column(Numeric, nullable=False)
    brokerage_bps = Column(Numeric, nullable=False)
    slippage_bps = Column(Numeric, nullable=False)
    fill_rule = Column(String, nullable=False)
    status = Column(String, nullable=False)
    error = Column(String, nullable=True)
    net_pnl = Column(Numeric, nullable=False)
    return_pct = Column(Numeric, nullable=False)
    ending_equity = Column(Numeric, nullable=False)
    max_drawdown_pct = Column(Numeric, nullable=False)
    n_trades = Column(Integer, nullable=False)
    n_wins = Column(Integer, nullable=False)
    n_losses = Column(Integer, nullable=False)
    win_rate = Column(Numeric, nullable=False)
    fees_paid = Column(Numeric, nullable=False)
    trades_json = Column(JSON, nullable=False)
