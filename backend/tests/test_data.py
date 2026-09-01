import pytest
import time
import pandas as pd
from backend.app.infrastructure.broker.fake import FakeBroker
from backend.app.infrastructure.data.downloader import DataDownloader
from backend.app.infrastructure.data.cache import ParquetCache

def test_downloader_initialization():
    broker = FakeBroker()
    downloader = DataDownloader(broker)
    
    # January 1, 2023 to January 1, 2024
    start_ms = 1672531200000 
    end_ms = 1704067200000
    
    # Our FakeBroker returns an empty list for historical data.
    # The goal of this test is to ensure the Downloader math loops correctly 
    # (chunking 365 days into 90 day pieces) without crashing,
    # and that the Cache handles the empty result gracefully.
    df = downloader.download_history("INFY-EQ", "1", start_ms, end_ms)
    assert isinstance(df, pd.DataFrame)
    assert df.empty
