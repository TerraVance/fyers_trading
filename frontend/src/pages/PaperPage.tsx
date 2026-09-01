import React, { useState, useEffect } from 'react';
import { Play, Square, Activity, DollarSign, Briefcase, Zap, Loader } from 'lucide-react';

const PaperPage = () => {
  const [strategyName, setStrategyName] = useState('SmaMomentumStrategy');
  const [symbol, setSymbol] = useState('NSE:INFY-EQ');
  const [resolution, setResolution] = useState('1');
  
  const [isRunning, setIsRunning] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  
  const [portfolio, setPortfolio] = useState<any>(null);

  const fetchPortfolio = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/paper/portfolio?strategy_name=${strategyName}&symbol=${symbol}`);
      const data = await res.json();
      if (data.success && data.is_running) {
        setIsRunning(true);
        setPortfolio(data.data);
      } else {
        setIsRunning(false);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchPortfolio, 1000); // Poll every second for live updates
    return () => clearInterval(interval);
  }, [strategyName, symbol]);

  const handleStart = async () => {
    setStatusMsg('Starting engine...');
    const res = await fetch('http://localhost:8000/api/v1/paper/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy_name: strategyName, symbol, resolution })
    });
    const data = await res.json();
    setStatusMsg(data.message);
    if (data.success) {
      setIsRunning(true);
      fetchPortfolio();
    }
  };

  const handleStop = async () => {
    const res = await fetch('http://localhost:8000/api/v1/paper/stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy_name: strategyName, symbol, resolution })
    });
    const data = await res.json();
    setStatusMsg(data.message);
    if (data.success) {
      setIsRunning(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">Live Engine (Paper Mode)</h1>
      <p className="page-subtitle">Stream live data through your strategy and execute virtual trades in real-time.</p>
      
      <div className="glass-panel" style={{ display: 'flex', gap: '20px', alignItems: 'flex-end', marginBottom: '24px' }}>
        <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
          <label>Strategy Class Name</label>
          <input type="text" className="input-field" value={strategyName} onChange={(e) => setStrategyName(e.target.value)} disabled={isRunning} />
        </div>
        <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
          <label>Symbol</label>
          <input type="text" className="input-field" value={symbol} onChange={(e) => setSymbol(e.target.value)} disabled={isRunning} />
        </div>
        <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
          <label>Resolution</label>
          <input type="text" className="input-field" value={resolution} onChange={(e) => setResolution(e.target.value)} disabled={isRunning} />
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          {!isRunning ? (
            <button className="btn-primary" onClick={handleStart} style={{ height: '46px', padding: '0 24px' }}>
              <Play size={16} style={{ display: 'inline', marginRight: '8px' }} /> Start Stream
            </button>
          ) : (
            <button className="btn-danger" onClick={handleStop} style={{ height: '46px', padding: '0 24px', background: 'var(--danger)', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>
              <Square size={16} style={{ display: 'inline', marginRight: '8px' }} /> Stop Engine
            </button>
          )}
        </div>
      </div>
      
      {statusMsg && <div style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>System: {statusMsg}</div>}

      {isRunning && (
         <div style={{ color: 'var(--success)', marginBottom: '24px', display: 'flex', alignItems: 'center' }}>
            <Activity size={18} style={{ marginRight: '8px' }} /> Engine is actively streaming and processing live signals...
         </div>
      )}

      {portfolio && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '24px', marginBottom: '32px' }}>
            <div className="glass-panel" style={{ textAlign: 'center' }}>
              <DollarSign size={24} color="var(--accent-color)" style={{ marginBottom: '8px' }} />
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Virtual Cash</div>
              <div style={{ fontSize: '2rem', fontWeight: 600 }}>₹{portfolio.current_cash.toFixed(2)}</div>
            </div>
            
            <div className="glass-panel" style={{ textAlign: 'center' }}>
              <Briefcase size={24} color="var(--text-primary)" style={{ marginBottom: '8px' }} />
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Open Positions</div>
              <div style={{ fontSize: '2rem', fontWeight: 600 }}>{portfolio.open_positions.length}</div>
            </div>
            
            <div className="glass-panel" style={{ textAlign: 'center' }}>
              <Zap size={24} color="var(--success)" style={{ marginBottom: '8px' }} />
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Total Equity</div>
              <div style={{ fontSize: '2rem', fontWeight: 600 }}>
                ₹{ (portfolio.current_cash + portfolio.open_positions.reduce((sum: number, p: any) => sum + (p.qty * p.entry_price), 0)).toFixed(2) }
              </div>
            </div>
          </div>
          
          <h2 style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>Live Order Book</h2>
          <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead style={{ background: 'rgba(255,255,255,0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <tr>
                  <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Time</th>
                  <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Action</th>
                  <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Qty</th>
                  <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Price</th>
                  <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Realized PnL</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.trades.map((trade: any, i: number) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                    <td style={{ padding: '16px' }}>{new Date(trade.time).toLocaleString()}</td>
                    <td style={{ padding: '16px', color: trade.type === 'BUY' ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>{trade.type}</td>
                    <td style={{ padding: '16px' }}>{trade.qty.toFixed(4)}</td>
                    <td style={{ padding: '16px' }}>₹{trade.price.toFixed(2)}</td>
                    <td style={{ padding: '16px', color: trade.pnl > 0 ? 'var(--success)' : (trade.pnl < 0 ? 'var(--danger)' : 'var(--text-primary)') }}>
                      {trade.pnl === 0 ? '-' : `₹${trade.pnl.toFixed(2)}`}
                    </td>
                  </tr>
                ))}
                {portfolio.trades.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-secondary)' }}>Listening for live signals... No trades yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default PaperPage;
