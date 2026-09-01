import pytest
import pandas as pd
from unittest.mock import patch
from backend.app.core.engine.backtest import BacktestEngine

@patch("backend.app.infrastructure.data.cache.ParquetCache.load_data")
def test_backtest_engine_run(mock_load_data):
    # Create dummy data simulating 100 periods
    # We need enough data to trigger the slow SMA (period 50)
    
    # Let's engineer a clear BUY and then a SELL.
    # Start at 100. Fast crosses above slow -> BUY at 150
    # Then price drops -> Fast crosses below slow -> SELL at 120
    close_prices = [100.0] * 55 + [150.0] * 10 + [120.0] * 10
    
    data = {
        'symbol': ['INFY-EQ'] * len(close_prices),
        'close': close_prices
    }
    # Index must be Epoch MS (increasing)
    df = pd.DataFrame(data, index=range(1000, 1000 + len(close_prices)))
    
    mock_load_data.return_value = df
    
    engine = BacktestEngine(initial_capital=10000.0)
    
    # Run backtest using the hand-coded SMA strategy
    result = engine.run("SmaMomentumStrategy", "INFY-EQ", "1", 0, 9999)
    
    assert result["success"] is True, result.get("error")
    metrics = result["metrics"]
    
    assert "total_return_pct" in metrics
    assert "win_rate_pct" in metrics
    assert "max_drawdown_pct" in metrics
    assert "profit_factor" in metrics
    assert "total_trades" in metrics
    assert "sharpe_ratio" in metrics
    assert "cagr_pct" in metrics
    assert "var_95_pct" in metrics
    assert "cvar_95_pct" in metrics
    assert "mc_worst_5_pct" in metrics
    assert "avg_duration_bars" in metrics
    assert "avg_mae_pct" in metrics
    assert "avg_mfe_pct" in metrics
    
    assert "chart_data" in result
    assert "execution_log" in result
