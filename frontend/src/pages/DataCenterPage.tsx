import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { DownloadCloud, CheckCircle, AlertTriangle, Loader, Search } from 'lucide-react';

interface SymbolSuggestion {
  symbol: string;
  name: string;
}

const DataCenterPage = () => {
  const [symbol, setSymbol] = useState('NSE:INFY-EQ');
  const [suggestions, setSuggestions] = useState<SymbolSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggestionRef = useRef<HTMLDivElement>(null);
  
  const [resolution, setResolution] = useState('1');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-01-01');
  const [status, setStatus] = useState<{type: 'idle' | 'loading' | 'success' | 'error', message: string}>({ type: 'idle', message: '' });
  const navigate = useNavigate();

  // Fetch suggestions when symbol text changes
  useEffect(() => {
    if (!symbol || symbol.length < 2 || !showSuggestions) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/data/symbols?query=${symbol}`);
        const data = await res.json();
        if (res.ok && data.success) {
          setSuggestions(data.items);
        }
      } catch (err) {
        console.error("Failed to fetch symbols", err);
      }
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [symbol, showSuggestions]);

  // Click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionRef.current && !suggestionRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleDownload = async () => {
    setStatus({ type: 'loading', message: 'Downloading data... (This may take a while depending on rate limits)' });
    
    // Convert YYYY-MM-DD to Epoch MS
    const startMs = new Date(startDate).getTime();
    const endMs = new Date(endDate).getTime();

    try {
      const res = await fetch('http://localhost:8000/api/v1/data/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          symbol, 
          resolution, 
          start_ms: startMs, 
          end_ms: endMs 
        })
      });
      
      const data = await res.json();
      
      if (res.ok && data.success) {
        // Snap the UI dates to the *actual* available dates that Fyers returned
        if (data.actual_start_ms && data.actual_end_ms) {
          setStartDate(new Date(data.actual_start_ms).toISOString().split('T')[0]);
          setEndDate(new Date(data.actual_end_ms).toISOString().split('T')[0]);
        }
        
        setStatus({ type: 'success', message: `${data.message} (${data.rows_downloaded} rows saved to Parquet). Dates adjusted to nearest valid trading days.` });
      } else {
        setStatus({ type: 'error', message: data.detail || 'Download failed. Check backend logs.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Network error. Make sure FastAPI is running.' });
    }
  };

  const setMaxHistory = () => {
    // Fyers generally provides history from roughly 2000 for daily, 2018 for intraday, etc.
    // Setting 1995 covers the maximum possible inception date for NSE.
    setStartDate('1995-01-01');
    setEndDate(new Date().toISOString().split('T')[0]);
  };

  return (
    <div>
      <h1 className="page-title">Data Center</h1>
      <p className="page-subtitle">Download and cache historical market data as highly compressed Parquet files.</p>
      
      <div className="glass-panel">
        <h3>Historical Downloader</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
          This engine automatically chunks massive date ranges into Fyers-compliant 100-day blocks and respects API rate limits.
        </p>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div className="form-group" style={{ position: 'relative' }} ref={suggestionRef}>
            <label>Symbol</label>
            <div style={{ position: 'relative' }}>
              <input 
                type="text" 
                className="input-field" 
                value={symbol}
                onFocus={() => setShowSuggestions(true)}
                onChange={(e) => {
                  setSymbol(e.target.value);
                  setShowSuggestions(true);
                }}
              />
              <Search size={16} style={{ position: 'absolute', right: '12px', top: '12px', color: 'var(--text-secondary)' }} />
            </div>
            
            {showSuggestions && suggestions.length > 0 && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                background: '#1a1d24', // Solid background to prevent text overlapping
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                marginTop: '4px',
                maxHeight: '250px',
                overflowY: 'auto',
                zIndex: 999, // Ensure it's above all other form elements
                boxShadow: '0 8px 16px rgba(0,0,0,0.6)'
              }}>
                {suggestions.map((item, idx) => (
                  <div 
                    key={idx}
                    style={{
                      padding: '10px 14px',
                      cursor: 'pointer',
                      borderBottom: '1px solid var(--border-color)',
                    }}
                    onClick={() => {
                      setSymbol(item.symbol);
                      setShowSuggestions(false);
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.1)')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <div style={{ fontWeight: '600', color: 'var(--text-primary)', fontSize: '14px' }}>{item.symbol}</div>
                    <div style={{ fontSize: '12px', color: 'var(--primary-color)', marginTop: '2px' }}>{item.name}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="form-group">
            <label>Resolution</label>
            <select 
              className="input-field" 
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
              style={{ appearance: 'auto' }}
            >
              <optgroup label="Intraday">
                <option value="1">1 Minute</option>
                <option value="2">2 Minutes</option>
                <option value="3">3 Minutes</option>
                <option value="5">5 Minutes</option>
                <option value="10">10 Minutes</option>
                <option value="15">15 Minutes</option>
                <option value="20">20 Minutes</option>
                <option value="30">30 Minutes</option>
                <option value="60">1 Hour (60m)</option>
                <option value="120">2 Hours (120m)</option>
                <option value="240">4 Hours (240m)</option>
              </optgroup>
              <optgroup label="Historical">
                <option value="D">1 Day (D)</option>
              </optgroup>
            </select>
          </div>
          <div className="form-group">
            <label>Start Date</label>
            <input 
              type="date" 
              className="input-field" 
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>End Date</label>
            <input 
              type="date" 
              className="input-field" 
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
          <button 
            className="btn-primary" 
            onClick={handleDownload}
            disabled={status.type === 'loading'}
          >
            {status.type === 'loading' ? (
              <><Loader size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} /> Processing...</>
            ) : (
              <><DownloadCloud size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} /> Fetch History</>
            )}
          </button>

          <button 
            className="btn-secondary" 
            onClick={setMaxHistory}
            disabled={status.type === 'loading'}
            style={{ 
              background: 'transparent', 
              border: '1px solid var(--primary-color)', 
              color: 'var(--primary-color)',
              padding: '8px 16px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 500
            }}
          >
            Max Available Data
          </button>
        </div>

        {status.message && (
          <div style={{ marginTop: '20px' }}>
            <span className={`status-badge ${status.type === 'success' ? 'status-success' : status.type === 'error' ? 'status-error' : ''}`}>
              {status.type === 'success' && <CheckCircle size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />}
              {status.type === 'error' && <AlertTriangle size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />}
              {status.message}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataCenterPage;
