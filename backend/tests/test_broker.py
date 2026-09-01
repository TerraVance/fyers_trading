import pytest
from backend.app.infrastructure.broker.fake import FakeBroker
from backend.app.infrastructure.broker.base import OrderIntent

def test_fake_broker_place_order():
    broker = FakeBroker()
    
    intent = OrderIntent(
        symbol="INFY-EQ",
        exchange="NSE",
        qty=10,
        side="BUY",
        order_type="MARKET",
        product="CNC"
    )
    
    # Place order
    order_id = broker.place_order(intent)
    assert order_id.startswith("FAKE_")
    
    # Get status
    status = broker.get_order_status(order_id)
    assert status == "FILLED"
