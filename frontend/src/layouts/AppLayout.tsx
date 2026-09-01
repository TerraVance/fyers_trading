import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, Database, Cpu, TrendingUp, Zap, ShieldAlert } from 'lucide-react';

const AppLayout = ({ children }: { children: React.ReactNode }) => {
  const [killSwitchEngaged, setKillSwitchEngaged] = useState(false);

  const triggerKillSwitch = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/risk/kill', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setKillSwitchEngaged(true);
        alert('GLOBAL KILL SWITCH ENGAGED! All engines halted. Liquidating positions.');
      }
    } catch (e) {
      alert('Error triggering Kill Switch!');
    }
  };

  const resetRiskGuard = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/risk/reset', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setKillSwitchEngaged(false);
        alert('Risk Guard Reset. Systems Online.');
      }
    } catch (e) {
      alert('Error resetting Risk Guard!');
    }
  };

  return (
    <div className="layout">
      <div className="sidebar">
        <h2>Consistent</h2>
        <NavLink to="/" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <Activity size={20} /> Broker Setup
        </NavLink>
        <NavLink to="/data" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <Database size={20} /> Data Center
        </NavLink>
        <NavLink to="/strategy" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <Cpu size={20} /> AI Strategy Lab
        </NavLink>
        <NavLink to="/backtest" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <TrendingUp size={20} /> Backtest Engine
        </NavLink>
        <NavLink to="/paper" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <Zap size={20} /> Live Paper Engine
        </NavLink>
        <NavLink to="/live" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
          <Activity size={20} color="var(--danger)" /> REAL Live Engine
        </NavLink>
      </div>
      <div className="main-content" style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '16px 32px', background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-color)' }}>
          {!killSwitchEngaged ? (
            <button onClick={triggerKillSwitch} style={{ display: 'flex', alignItems: 'center', background: 'var(--danger)', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', boxShadow: '0 0 15px rgba(255, 68, 68, 0.4)' }}>
              <ShieldAlert size={18} style={{ marginRight: '8px' }} /> GLOBAL KILL SWITCH
            </button>
          ) : (
            <button onClick={resetRiskGuard} style={{ display: 'flex', alignItems: 'center', background: 'var(--success)', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              <ShieldAlert size={18} style={{ marginRight: '8px' }} /> RESET RISK GUARD
            </button>
          )}
        </div>
        <div style={{ padding: '32px', overflowY: 'auto', flex: 1 }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default AppLayout;
