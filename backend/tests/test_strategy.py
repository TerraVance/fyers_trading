import pytest
import pandas as pd
from backend.app.strategies.sma_momentum_strategy import SmaMomentumStrategy

def test_sma_strategy_buy_signal():
    data = {
        'symbol': ['INFY-EQ'] * 20,
        'close': [100.0] * 19 + [500.0] # Massive spike on the very last candle
    }
    df = pd.DataFrame(data)
    
    strategy = SmaMomentumStrategy(fast_period=5, slow_period=10)
    df_result = strategy.generate_signals(df)
    
    assert 'signal' in df_result.columns
    # Check that the last row triggered a BUY
    assert df_result.iloc[-1]['signal'] == "BUY"
    # Check that previous rows are None
    assert pd.isna(df_result.iloc[-2]['signal'])
