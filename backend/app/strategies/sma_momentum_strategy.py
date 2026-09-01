import pandas as pd
from ta.trend import SMAIndicator
from backend.app.core.strategy.base import AbstractStrategy

class SmaMomentumStrategy(AbstractStrategy):
    """
    A vectorized SMA crossover strategy template.
    Generates a BUY signal when the fast SMA crosses above the slow SMA.
    Generates a SELL signal when the fast SMA crosses below the slow SMA.
    """
    def __init__(self, fast_period: int = 10, slow_period: int = 50):
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < self.slow_period:
            df['signal'] = None
            return df

        # Ensure close is float
        df['close'] = df['close'].astype(float)
        
        # Calculate indicators
        fast_sma = SMAIndicator(close=df['close'], window=self.fast_period)
        slow_sma = SMAIndicator(close=df['close'], window=self.slow_period)
        
        df['sma_fast'] = fast_sma.sma_indicator()
        df['sma_slow'] = slow_sma.sma_indicator()

        df['signal'] = None

        # Vectorized crossover conditions
        buy_condition = (df['sma_fast'] > df['sma_slow']) & (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1))
        sell_condition = (df['sma_fast'] < df['sma_slow']) & (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1))
        
        df.loc[buy_condition, 'signal'] = "BUY"
        df.loc[sell_condition, 'signal'] = "SELL"
            
        return df
