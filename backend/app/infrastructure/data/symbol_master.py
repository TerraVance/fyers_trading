import csv
import urllib.request
import io
import threading
from typing import List, Dict

class SymbolMaster:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SymbolMaster, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.symbols: List[Dict[str, str]] = []
        self._is_loaded = False
        self._load_lock = threading.Lock()
        self._initialized = True

    def _fetch_exchange(self, url: str) -> None:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                if len(row) >= 14:
                    # Index 1 is Company Name / Symbol Details
                    # Index 9 is Fyers Broker Symbol
                    company_name = row[1].strip()
                    fyers_symbol = row[9].strip()
                    if fyers_symbol:
                        self.symbols.append({
                            "symbol": fyers_symbol,
                            "name": company_name
                        })
        except Exception as e:
            print(f"Error fetching symbols from {url}: {e}")

    def load_symbols(self) -> None:
        """Downloads the symbol masters. Thread-safe to run once."""
        with self._load_lock:
            if self._is_loaded:
                return
                
            print("Downloading Fyers symbol master lists...")
            # We fetch NSE and BSE cash markets by default
            urls = [
                "https://public.fyers.in/sym_details/NSE_CM.csv",
                "https://public.fyers.in/sym_details/BSE_CM.csv"
            ]
            for url in urls:
                self._fetch_exchange(url)
            
            print(f"Loaded {len(self.symbols)} total symbols.")
            self._is_loaded = True

    def search(self, query: str, limit: int = 50) -> List[Dict[str, str]]:
        if not self._is_loaded:
            self.load_symbols()
            
        if not query:
            return self.symbols[:limit]
            
        query = query.lower()
        results = []
        
        for item in self.symbols:
            symbol_lower = item['symbol'].lower()
            name_lower = item['name'].lower()
            
            if query in symbol_lower or query in name_lower:
                results.append(item)
                if len(results) >= limit:
                    break
                    
        return results

# Singleton instance
symbol_master = SymbolMaster()
