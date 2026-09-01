from abc import ABC, abstractmethod
import pandas as pd

class AbstractStrategy(ABC):
    """
    The strict interface that all mathematical trading strategies must follow.
    The LLM will generate classes that inherit from this.
    """
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Accepts a dataframe of historical OHLCV data.
        Must return the dataframe with an added 'signal' column containing 'BUY', 'SELL', or None.
        Vectorized execution ensures backtests complete in milliseconds.
        """
        pass
