import pandas as pd
from typing import Optional
from backend.app.infrastructure.broker.base import AbstractBroker
from .cache import ParquetCache
from backend.app.utils.rate_limiter import rate_limit

# Fyers limit: 100 days maximum per request
MAX_DAYS_PER_REQUEST = 90
MS_PER_DAY = 24 * 60 * 60 * 1000

class DataDownloader:
    def __init__(self, broker: AbstractBroker):
        self.broker = broker
        self.cache = ParquetCache()

    @rate_limit(calls_per_second=3.0) # 3 requests per second max
    def _fetch_chunk(self, symbol: str, resolution: str, start: int, end: int):
        # Convert ms to seconds for Fyers API
        start_s = start // 1000
        end_s = end // 1000
        return self.broker.get_historical_candles(symbol, resolution, start_s, end_s)

    def download_history(self, symbol: str, resolution: str, start_ms: int, end_ms: int) -> pd.DataFrame:
        metadata = self.cache.get_metadata(symbol, resolution)
        
        fetch_start = start_ms
        fetch_end = end_ms
        
        existing_df = None
        if metadata:
            cached_start = metadata["start_time_ms"]
            cached_end = metadata["end_time_ms"]
            
            # If the requested range is completely inside the cache, just load and return it
            if start_ms >= cached_start and end_ms <= cached_end:
                existing_df = self.cache.load_data(symbol, resolution)
                mask = (existing_df['time'] >= pd.to_datetime(start_ms, unit='ms')) & (existing_df['time'] <= pd.to_datetime(end_ms, unit='ms'))
                return existing_df.loc[mask]
                
            # If we need older data, extend fetch_start back
            # If we need newer data, extend fetch_end forward
            fetch_start = min(start_ms, cached_start)
            fetch_end = max(end_ms, cached_end)
            existing_df = self.cache.load_data(symbol, resolution)

        all_candles = []
        current = fetch_start
        
        while current < fetch_end:
            chunk_end = min(current + (MAX_DAYS_PER_REQUEST * MS_PER_DAY), fetch_end)
            
            # Optimization: Skip chunk if it falls entirely within cached range
            if metadata and current >= metadata["start_time_ms"] and chunk_end <= metadata["end_time_ms"]:
                current = chunk_end + MS_PER_DAY
                continue
                
            print(f"Fetching chunk {symbol} {resolution} from {current} to {chunk_end}")
            candles = self._fetch_chunk(symbol, resolution, current, chunk_end)
            all_candles.extend(candles)
            
            current = chunk_end + MS_PER_DAY

        new_df = pd.DataFrame(all_candles)
        
        if existing_df is not None and not new_df.empty:
            if 'time' in new_df.columns:
                new_df['time'] = pd.to_datetime(new_df['time'], unit='ms')
            combined = pd.concat([existing_df, new_df])
        elif existing_df is not None:
            combined = existing_df
        else:
            combined = new_df

        self.cache.save_data(symbol, resolution, combined)
        
        # Return the specifically requested window from the new clean cache
        final_df = self.cache.load_data(symbol, resolution)
        if final_df is None or final_df.empty:
            return pd.DataFrame()
            
        mask = (final_df['time'] >= pd.to_datetime(start_ms, unit='ms')) & (final_df['time'] <= pd.to_datetime(end_ms, unit='ms'))
        return final_df.loc[mask]
