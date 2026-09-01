import React, { useState } from 'react';
import { Play, Activity, TrendingUp, TrendingDown, Target, Zap, Loader, Table as TableIcon } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MetricCard = ({ label, value, type = 'neutral', postfix = '' }: any) => {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <span className={`metric-value ${type}`}>{value}{postfix}</span>
    </div>
  );
};

const BacktestPage = () => {
  const [strategyName, setStrategyName] = useState('SmaMomentumStrategy');
  const [symbol, setSymbol] = useState('NSE:INFY-EQ');
  const [resolution, setResolution] = useState('1');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-01-01');
  
  const [status, setStatus] = useState<{type: 'idle' | 'loading' | 'success' | 'error', message: string}>({ type: 'idle', message: '' });
  const [metrics, setMetrics] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [executionLog, setExecutionLog] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'metrics' | 'log'>('metrics');

  const handleRun = async () => {
    setStatus({ type: 'loading', message: 'Running Institutional Quant Simulation...' });
    setMetrics(null);
    setChartData([]);
    setExecutionLog([]);
    
    const startMs = new Date(startDate).getTime();
    const endMs = new Date(endDate).getTime();

    try {
      const res = await fetch('http://localhost:8000/api/v1/backtest/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy_name: strategyName, symbol, resolution, start_ms: startMs, end_ms: endMs })
      });
      
      const data = await res.json();
      
      if (res.ok && data.success) {
        setStatus({ type: 'success', message: 'Simulation complete.' });
        setMetrics(data.metrics);
        
        const formattedChartData = (data.chart_data || []).map((d: any) => ({
          ...d,
          date: new Date(d.time).toLocaleDateString()
        }));
        setChartData(formattedChartData);
        setExecutionLog(data.execution_log || []);
      } else {
        setStatus({ type: 'error', message: data.detail || 'Backtest failed. Check logs.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Network error. Make sure FastAPI is running.' });
    }
  };

  return (
    <div>
      <h1 className="page-title">Institutional Quant Engine</h1>
      <p className="page-subtitle">Run multi-year simulations with Fyers commission drag and Wall Street-grade statistical validation.</p>
      
      <div className="glass-panel">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
          <div className="form-group">
            <label>Strategy Class Name</label>
            <input type="text" className="input-field" value={strategyName} onChange={(e) => setStrategyName(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Symbol</label>
            <input type="text" className="input-field" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Resolution</label>
            <input type="text" className="input-field" value={resolution} onChange={(e) => setResolution(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Start Date</label>
            <input type="date" className="input-field" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label>End Date</label>
            <input type="date" className="input-field" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
             <button className="btn-primary" onClick={handleRun} disabled={status.type === 'loading'} style={{ width: '100%', height: '46px' }}>
              {status.type === 'loading' ? (
                <><Loader size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} /> Simulating...</>
              ) : (
                <><Play size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} /> Run Simulation</>
              )}
            </button>
          </div>
        </div>
        
        {status.type === 'error' && (
           <div style={{ marginTop: '16px', color: 'var(--danger)' }}>{status.message}</div>
        )}
      </div>

      {metrics && (
        <>
          {/* Charts Section */}
          <div style={{ display: 'flex', gap: '24px', marginTop: '32px' }}>
            <div className="glass-panel" style={{ flex: 2, padding: '24px' }}>
              <h3 style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>Equity Curve</h3>
              <div style={{ height: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--accent-color)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="var(--accent-color)" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="date" stroke="var(--text-secondary)" fontSize={12} tickLine={false} />
                    <YAxis domain={['auto', 'auto']} stroke="var(--text-secondary)" fontSize={12} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--glass-bg)', border: 'var(--glass-border)', borderRadius: '8px' }}
                      itemStyle={{ color: 'var(--text-primary)' }}
                    />
                    <Area type="monotone" dataKey="equity" stroke="var(--accent-color)" fillOpacity={1} fill="url(#colorEquity)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="glass-panel" style={{ flex: 1, padding: '24px' }}>
              <h3 style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>Underwater Plot (Drawdown)</h3>
              <div style={{ height: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--danger)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="var(--danger)" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="date" stroke="var(--text-secondary)" fontSize={12} tickLine={false} hide />
                    <YAxis stroke="var(--text-secondary)" fontSize={12} tickLine={false} tickFormatter={(val) => `${val}%`} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--glass-bg)', border: 'var(--glass-border)', borderRadius: '8px' }}
                    />
                    <Area type="step" dataKey="drawdown" stroke="var(--danger)" fillOpacity={1} fill="url(#colorDrawdown)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '16px', marginTop: '24px', borderBottom: '1px solid var(--border-color)' }}>
            <button 
              style={{ background: 'none', border: 'none', color: activeTab === 'metrics' ? 'var(--accent-color)' : 'var(--text-secondary)', padding: '12px 24px', fontSize: '1rem', fontWeight: 600, borderBottom: activeTab === 'metrics' ? '2px solid var(--accent-color)' : 'none', cursor: 'pointer' }}
              onClick={() => setActiveTab('metrics')}
            >
              <Activity size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'text-bottom' }} /> Metrics Tear-Sheet
            </button>
            <button 
              style={{ background: 'none', border: 'none', color: activeTab === 'log' ? 'var(--accent-color)' : 'var(--text-secondary)', padding: '12px 24px', fontSize: '1rem', fontWeight: 600, borderBottom: activeTab === 'log' ? '2px solid var(--accent-color)' : 'none', cursor: 'pointer' }}
              onClick={() => setActiveTab('log')}
            >
              <TableIcon size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'text-bottom' }} /> Execution Log
            </button>
          </div>

          {activeTab === 'metrics' && (
            <div style={{ marginTop: '24px' }}>
              <h2 style={{ marginBottom: '8px', fontSize: '1.2rem', color: 'var(--text-secondary)' }}><Activity size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '8px' }} /> Return Analytics</h2>
              <div className="metrics-grid">
                <MetricCard label="Total Return" value={metrics.total_return_pct} postfix="%" type={metrics.total_return_pct >= 0 ? 'positive' : 'negative'} />
                <MetricCard label="CAGR" value={metrics.cagr_pct} postfix="%" type={metrics.cagr_pct >= 0 ? 'positive' : 'negative'} />
                <MetricCard label="Win Rate" value={metrics.win_rate_pct} postfix="%" type={metrics.win_rate_pct >= 50 ? 'positive' : 'negative'} />
                <MetricCard label="Profit Factor" value={metrics.profit_factor} type={metrics.profit_factor >= 1.2 ? 'positive' : 'negative'} />
              </div>
              
              <h2 style={{ marginTop: '32px', marginBottom: '8px', fontSize: '1.2rem', color: 'var(--text-secondary)' }}><TrendingDown size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '8px' }} /> Risk vs Reward Ratios</h2>
              <div className="metrics-grid">
                <MetricCard label="Max Drawdown" value={metrics.max_drawdown_pct} postfix="%" type={metrics.max_drawdown_pct < -15 ? 'negative' : 'neutral'} />
                <MetricCard label="Sharpe Ratio" value={metrics.sharpe_ratio} type={metrics.sharpe_ratio > 1 ? 'positive' : 'neutral'} />
                <MetricCard label="Sortino Ratio" value={metrics.sortino_ratio} type={metrics.sortino_ratio > 1.5 ? 'positive' : 'neutral'} />
                <MetricCard label="Calmar Ratio" value={metrics.calmar_ratio} type={metrics.calmar_ratio > 1 ? 'positive' : 'neutral'} />
              </div>

              <h2 style={{ marginTop: '32px', marginBottom: '8px', fontSize: '1.2rem', color: 'var(--text-secondary)' }}><Target size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '8px' }} /> Trade Diagnostics</h2>
              <div className="metrics-grid">
                <MetricCard label="Expectancy" value={metrics.expectancy_pct} postfix="%" type={metrics.expectancy_pct > 0 ? 'positive' : 'negative'} />
                <MetricCard label="Avg Win" value={metrics.avg_win_pct} postfix="%" type="positive" />
                <MetricCard label="Avg Loss" value={metrics.avg_loss_pct} postfix="%" type="negative" />
                <MetricCard label="Avg Duration (Bars)" value={metrics.avg_duration_bars} type="neutral" />
              </div>
              
              <h2 style={{ marginTop: '32px', marginBottom: '8px', fontSize: '1.2rem', color: 'var(--text-secondary)' }}><Zap size={18} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '8px' }} /> Anti-Overfitting & Execution</h2>
              <div className="metrics-grid">
                <MetricCard label="Monte Carlo 5% (Worst Case)" value={metrics.mc_worst_5_pct} postfix="%" type={metrics.mc_worst_5_pct > 0 ? 'positive' : 'negative'} />
                <MetricCard label="VaR (95%)" value={metrics.var_95_pct} postfix="%" type="neutral" />
                <MetricCard label="Avg MAE (Adverse Heat)" value={metrics.avg_mae_pct} postfix="%" type="negative" />
                <MetricCard label="Avg MFE (Profit Left)" value={metrics.avg_mfe_pct} postfix="%" type="positive" />
              </div>
            </div>
          )}

          {activeTab === 'log' && (
            <div className="glass-panel" style={{ marginTop: '24px', padding: 0, overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead style={{ background: 'rgba(255,255,255,0.05)', borderBottom: '1px solid var(--border-color)' }}>
                  <tr>
                    <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Entry Time</th>
                    <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Entry Price</th>
                    <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Exit Time</th>
                    <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Exit Price</th>
                    <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Bars</th>
                    <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>MAE %</th>
                    <th style={{ padding: '16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Net PnL %</th>
                  </tr>
                </thead>
                <tbody>
                  {executionLog.map((log, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                      <td style={{ padding: '16px' }}>{new Date(log.entry_time).toLocaleString()}</td>
                      <td style={{ padding: '16px' }}>₹{log.entry_price}</td>
                      <td style={{ padding: '16px' }}>{new Date(log.exit_time).toLocaleString()}</td>
                      <td style={{ padding: '16px' }}>₹{log.exit_price}</td>
                      <td style={{ padding: '16px' }}>{log.duration_bars}</td>
                      <td style={{ padding: '16px', color: 'var(--danger)' }}>{log.mae_pct}%</td>
                      <td style={{ padding: '16px', color: log.profit_loss_pct >= 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>{log.profit_loss_pct}%</td>
                    </tr>
                  ))}
                  {executionLog.length === 0 && (
                    <tr>
                      <td colSpan={7} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-secondary)' }}>No trades executed in this period.</td>
                    </tr>
                  )}
                </tbody>
              </table>
              <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Showing last 100 trades for UI performance.
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default BacktestPage;
