import os
import json
import pandas as pd
from typing import Optional, Dict, Any

# Root directory + backend/data_cache
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data_cache")
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")

class ParquetCache:
    def __init__(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        if not os.path.exists(MANIFEST_PATH):
            with open(MANIFEST_PATH, "w") as f:
                json.dump({}, f)

    def _load_manifest(self) -> Dict[str, Any]:
        with open(MANIFEST_PATH, "r") as f:
            return json.load(f)

    def _save_manifest(self, manifest: Dict[str, Any]):
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=4)

    def get_metadata(self, symbol: str, resolution: str) -> Optional[Dict[str, Any]]:
        manifest = self._load_manifest()
        key = f"{symbol}_{resolution}"
        return manifest.get(key)

    def load_data(self, symbol: str, resolution: str) -> pd.DataFrame:
        file_path = os.path.join(CACHE_DIR, f"{symbol}_{resolution}.parquet")
        if os.path.exists(file_path):
            return pd.read_parquet(file_path)
        return pd.DataFrame()

    def save_data(self, symbol: str, resolution: str, df: pd.DataFrame):
        if df.empty:
            return
            
        # Ensure timestamp is datetime and sort
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'], unit='ms')
        
        # Deduplicate and sort
        df = df.sort_values('time').drop_duplicates(subset=['time']).reset_index(drop=True)

        file_path = os.path.join(CACHE_DIR, f"{symbol}_{resolution}.parquet")
        df.to_parquet(file_path, index=False)

        # Update manifest
        manifest = self._load_manifest()
        key = f"{symbol}_{resolution}"
        manifest[key] = {
            "start_time_ms": int(df['time'].iloc[0].timestamp() * 1000),
            "end_time_ms": int(df['time'].iloc[-1].timestamp() * 1000),
            "rows": len(df)
        }
        self._save_manifest(manifest)
