import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.infrastructure.database.session import Base
from backend.app.infrastructure.database.repo import RecordsRepo
from backend.app.core.models import LiveSession, Order
import os

# Use a purely in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_repo_create_session(db):
    repo = RecordsRepo(db)
    
    session_data = LiveSession(
        mode="PAPER",
        strategy_name="sma_momentum",
        strategy_version="1.0.0",
        params_json="{}",
        symbols_json="[]",
        product="CNC",
        started_at_ms=1000,
        last_active_ms=1000,
        status="ACTIVE",
        state_file="dummy.json"
    )
    
    created = repo.create_session(session_data)
    assert created.id is not None
    assert created.strategy_name == "sma_momentum"
    
def test_repo_insert_order(db):
    repo = RecordsRepo(db)
    
    order_data = Order(
        mode="PAPER",
        session_id=None,
        placed_at_ms=1000,
        updated_at_ms=1000,
        strategy_name="sma_momentum",
        symbol="INFY",
        exchange="NSE",
        trading_symbol="INFY-EQ",
        token="1594",
        side="BUY",
        product="CNC",
        order_type="MARKET",
        qty=10,
        status="OPEN",
        signal_reason="RSI_CROSS"
    )
    
    created = repo.insert_order(order_data)
    assert created.id is not None
    assert created.symbol == "INFY"
    
    fetched = repo.get_order(created.id)
    assert fetched.qty == 10
