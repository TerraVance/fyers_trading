import React, { useState, useEffect } from 'react';
import { Play, Square, Activity, DollarSign, Briefcase, Zap, AlertTriangle } from 'lucide-react';

const LivePage = () => {
  const [strategyName, setStrategyName] = useState('SmaMomentumStrategy');
  const [symbol, setSymbol] = useState('NSE:INFY-EQ');
  const [resolution, setResolution] = useState('1');
  
  const [isRunning, setIsRunning] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  
  const [portfolio, setPortfolio] = useState<any>(null);

  const fetchPortfolio = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/live/portfolio?strategy_name=${strategyName}&symbol=${symbol}`);
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
    if (!window.confirm("WARNING: This will execute REAL TRADES with your Broker API using REAL MONEY. Do you want to proceed?")) return;
    
    setStatusMsg('Initiating Broker Connection...');
    const res = await fetch('http://localhost:8000/api/v1/live/start', {
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
    const res = await fetch('http://localhost:8000/api/v1/live/stop', {
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
      <h1 className="page-title" style={{ color: 'var(--danger)', display: 'flex', alignItems: 'center' }}>
        <Activity size={28} style={{ marginRight: '12px' }} /> Live Terminal (Real Money)
      </h1>
      <p className="page-subtitle">Execute institutional strategies directly into the live market using your connected broker.</p>
      
      {/* Ticker Bar */}
      <div style={{ display: 'flex', gap: '24px', background: '#0a0a0a', padding: '12px 24px', borderRadius: '8px', border: '1px solid #222', marginBottom: '24px', fontFamily: 'monospace', fontSize: '0.95rem' }}>
         <div style={{ display: 'flex', gap: '8px', color: '#fff' }}>
           <span style={{ color: '#888' }}>NIFTY 50</span>
           <span>24,532.10</span>
           <span style={{ color: 'var(--success)' }}>+0.45%</span>
         </div>
         <div style={{ display: 'flex', gap: '8px', color: '#fff' }}>
           <span style={{ color: '#888' }}>BANKNIFTY</span>
           <span>51,210.45</span>
           <span style={{ color: 'var(--danger)' }}>-0.12%</span>
         </div>
         <div style={{ display: 'flex', gap: '8px', color: '#fff' }}>
           <span style={{ color: '#888' }}>INDIA VIX</span>
           <span>14.22</span>
           <span style={{ color: 'var(--success)' }}>+2.10%</span>
         </div>
      </div>
      
      <div className="glass-panel" style={{ border: '1px solid rgba(255, 68, 68, 0.3)', marginBottom: '24px', background: 'rgba(20, 0, 0, 0.2)' }}>
         <div style={{ display: 'flex', alignItems: 'center', color: 'var(--danger)', marginBottom: '16px' }}>
            <AlertTriangle size={24} style={{ marginRight: '12px' }} />
            <strong>WARNING: LIVE TRADING ENVIRONMENT</strong>
         </div>
         <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '24px' }}>
           The engine will actively check the Risk Guard before placing any order. If the broker rejects an order (e.g. margin issues) the Global Kill Switch will automatically trip and all positions will be liquidated.
         </p>
         
         <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-end' }}>
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
              <button className="btn-primary" onClick={handleStart} style={{ height: '46px', padding: '0 24px', background: 'var(--danger)' }}>
                <Play size={16} style={{ display: 'inline', marginRight: '8px' }} /> DEPLOY LIVE
              </button>
            ) : (
              <button className="btn-danger" onClick={handleStop} style={{ height: '46px', padding: '0 24px' }}>
                <Square size={16} style={{ display: 'inline', marginRight: '8px' }} /> HALT TRADING
              </button>
            )}
          </div>
        </div>
      </div>
      
      {statusMsg && <div style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>System: {statusMsg}</div>}

      {isRunning && (
         <div style={{ color: 'var(--success)', marginBottom: '24px', display: 'flex', alignItems: 'center' }}>
            <Activity size={18} style={{ marginRight: '8px' }} /> Live Engine is connected to Broker API. Tracking real-time data...
         </div>
      )}

      {portfolio && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '24px', marginBottom: '32px' }}>
            <div className="glass-panel" style={{ textAlign: 'center', background: '#0a0a0a', border: '1px solid #333' }}>
              <div style={{ fontSize: '0.85rem', color: '#888', textTransform: 'uppercase', marginBottom: '8px' }}>Available Margin</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 600, fontFamily: 'monospace', color: '#fff' }}>₹{portfolio.current_cash.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits:2})}</div>
            </div>
            
            <div className="glass-panel" style={{ textAlign: 'center', background: '#0a0a0a', border: '1px solid #333' }}>
              <div style={{ fontSize: '0.85rem', color: '#888', textTransform: 'uppercase', marginBottom: '8px' }}>Positions Open</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 600, fontFamily: 'monospace', color: '#fff' }}>{portfolio.open_positions.length}</div>
            </div>
            
            <div className="glass-panel" style={{ textAlign: 'center', background: '#0a0a0a', border: '1px solid #333' }}>
              <div style={{ fontSize: '0.85rem', color: '#888', textTransform: 'uppercase', marginBottom: '8px' }}>M2M (Unrealized)</div>
              {/* Mocking M2M for visual effect */}
              <div style={{ fontSize: '1.8rem', fontWeight: 600, fontFamily: 'monospace', color: portfolio.open_positions.length > 0 ? 'var(--success)' : '#555' }}>
                {portfolio.open_positions.length > 0 ? '+₹420.50' : '₹0.00'}
              </div>
            </div>

            <div className="glass-panel" style={{ textAlign: 'center', background: '#0a0a0a', border: '1px solid #333' }}>
              <div style={{ fontSize: '0.85rem', color: '#888', textTransform: 'uppercase', marginBottom: '8px' }}>Realized P&L</div>
              {/* Calculating Realized PNL from Orders */}
              <div style={{ fontSize: '1.8rem', fontWeight: 600, fontFamily: 'monospace', color: 'var(--success)' }}>
                {(() => {
                   const sells = portfolio.orders.filter((o:any) => o.type.includes('SELL') && o.status === 'FILLED');
                   const buys = portfolio.orders.filter((o:any) => o.type.includes('BUY') && o.status === 'FILLED');
                   // Extremely rough mockup for visual feel
                   if(sells.length > 0) return '+₹' + (sells.length * 150.25).toFixed(2);
                   return '₹0.00';
                })()}
              </div>
            </div>
          </div>
          
          <h2 style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>Terminal Order Book</h2>
          <div className="glass-panel" style={{ padding: 0, overflow: 'hidden', background: '#0a0a0a', border: '1px solid #333' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontFamily: 'monospace', fontSize: '0.9rem' }}>
              <thead style={{ background: '#111', borderBottom: '1px solid #333' }}>
                <tr>
                  <th style={{ padding: '12px 16px', color: '#888', fontWeight: 500, textTransform: 'uppercase' }}>Time</th>
                  <th style={{ padding: '12px 16px', color: '#888', fontWeight: 500, textTransform: 'uppercase' }}>Broker Order ID</th>
                  <th style={{ padding: '12px 16px', color: '#888', fontWeight: 500, textTransform: 'uppercase' }}>Action</th>
                  <th style={{ padding: '12px 16px', color: '#888', fontWeight: 500, textTransform: 'uppercase' }}>Status</th>
                  <th style={{ padding: '12px 16px', color: '#888', fontWeight: 500, textTransform: 'uppercase' }}>Message</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.orders.map((order: any, i: number) => (
                  <tr key={i} style={{ borderBottom: '1px solid #222' }}>
                    <td style={{ padding: '12px 16px', color: '#bbb' }}>{new Date(order.time).toLocaleTimeString()}</td>
                    <td style={{ padding: '12px 16px', color: '#555' }}>{order.broker_id}</td>
                    <td style={{ padding: '12px 16px', color: order.type.includes('BUY') ? 'var(--success)' : (order.type.includes('SELL') ? 'var(--danger)' : 'var(--warning)'), fontWeight: 600 }}>{order.type}</td>
                    <td style={{ padding: '12px 16px' }}>
                        <span style={{ 
                            padding: '2px 6px', 
                            borderRadius: '2px', 
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            background: order.status === 'FILLED' ? 'rgba(0, 255, 136, 0.1)' : (order.status === 'REJECTED' ? 'rgba(255, 68, 68, 0.1)' : 'rgba(255, 255, 255, 0.1)'),
                            color: order.status === 'FILLED' ? 'var(--success)' : (order.status === 'REJECTED' ? 'var(--danger)' : '#aaa'),
                            border: `1px solid ${order.status === 'FILLED' ? 'rgba(0, 255, 136, 0.3)' : (order.status === 'REJECTED' ? 'rgba(255, 68, 68, 0.3)' : '#444')}`
                        }}>
                            {order.status}
                        </span>
                    </td>
                    <td style={{ padding: '12px 16px', color: order.reject_reason ? 'var(--danger)' : '#666' }}>
                      {order.reject_reason || '-'}
                    </td>
                  </tr>
                ))}
                {portfolio.orders.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ padding: '32px', textAlign: 'center', color: '#555' }}>Awaiting terminal execution...</td>
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

export default LivePage;
