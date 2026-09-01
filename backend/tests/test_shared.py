import pytest
from datetime import datetime
import zoneinfo
from backend.app.utils.time_utils import ist_to_utc_ms, utc_ms_to_ist
from backend.app.utils.watchlist import load_watchlist
from backend.app.core.models import Signal
from backend.app.core.errors import AppError

IST = zoneinfo.ZoneInfo("Asia/Kolkata")

def test_time_conversions():
    # 2024-01-01 09:15:00 IST
    dt_ist = datetime(2024, 1, 1, 9, 15, 0, tzinfo=IST)
    ts_ms = ist_to_utc_ms(dt_ist)
    
    # 09:15 IST is 03:45 UTC = 1704080700000 ms
    assert ts_ms == 1704080700000
    
    # Convert back
    dt_back = utc_ms_to_ist(ts_ms)
    assert dt_back == dt_ist
    assert dt_back.tzinfo == IST

def test_watchlist_loader(tmp_path):
    yaml_content = """
items:
  - symbol: "TEST"
    exchange: "NSE"
    token: "123"
    trading_symbol: "TEST-EQ"
    sync_1m: true
    sync_daily: false
    live: true
"""
    test_file = tmp_path / "test_watchlist.yaml"
    test_file.write_text(yaml_content)
    
    watchlist = load_watchlist(str(test_file))
    assert len(watchlist.items) == 1
    item = watchlist.items[0]
    assert item.symbol == "TEST"
    assert item.sync_1m is True
    assert item.sync_daily is False

def test_signal_model():
    signal = Signal(
        action="BUY",
        reason="RSI Crossover",
        stop_loss=1400.0,
        target=1500.0
    )
    assert signal.action == "BUY"
    assert signal.confidence == 1.0
    assert signal.trailing_stop_pct is None

def test_app_error():
    err = AppError("TEST_CODE", "Test message", 401)
    assert err.code == "TEST_CODE"
    assert err.message == "Test message"
    assert err.status_code == 401
