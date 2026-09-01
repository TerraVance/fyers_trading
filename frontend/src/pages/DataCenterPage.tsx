import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DownloadCloud, CheckCircle, AlertTriangle, Loader } from 'lucide-react';

const DataCenterPage = () => {
  const [symbol, setSymbol] = useState('NSE:INFY-EQ');
  const [resolution, setResolution] = useState('1');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-01-01');
  const [status, setStatus] = useState<{type: 'idle' | 'loading' | 'success' | 'error', message: string}>({ type: 'idle', message: '' });
  const navigate = useNavigate();

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
        setStatus({ type: 'success', message: `${data.message} (${data.rows_downloaded} rows saved to Parquet). Redirecting...` });
        setTimeout(() => navigate('/strategy'), 2000);
      } else {
        setStatus({ type: 'error', message: data.detail || 'Download failed. Check backend logs.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Network error. Make sure FastAPI is running.' });
    }
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
          <div className="form-group">
            <label>Symbol</label>
            <input 
              type="text" 
              className="input-field" 
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Resolution (Minutes)</label>
            <input 
              type="text" 
              className="input-field" 
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
            />
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
        
        <button 
          className="btn-primary" 
          onClick={handleDownload}
          disabled={status.type === 'loading'}
          style={{ marginTop: '16px' }}
        >
          {status.type === 'loading' ? (
            <><Loader size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} /> Processing...</>
          ) : (
            <><DownloadCloud size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} /> Fetch History</>
          )}
        </button>

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
