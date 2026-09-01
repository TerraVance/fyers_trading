import React, { useState } from 'react';
import { Cpu, CheckCircle, AlertTriangle, Code } from 'lucide-react';

const StrategyLabPage = () => {
  const [strategyName, setStrategyName] = useState('MyCustomStrategy');
  const [description, setDescription] = useState('Buy when the 14-period RSI crosses below 30 and MACD histogram is positive. Sell when RSI crosses above 70.');
  const [status, setStatus] = useState<{type: 'idle' | 'loading' | 'success' | 'error', message: string, filePath?: string}>({ type: 'idle', message: '' });

  const handleGenerate = async () => {
    setStatus({ type: 'loading', message: 'AI is writing your Python strategy... (This takes 5-10 seconds)' });
    
    try {
      const res = await fetch('http://localhost:8000/api/v1/strategy/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          strategy_name: strategyName, 
          description: description 
        })
      });
      
      const data = await res.json();
      
      if (res.ok && data.success) {
        setStatus({ 
          type: 'success', 
          message: data.message,
          filePath: data.file_path
        });
      } else {
        setStatus({ type: 'error', message: data.detail || 'Generation failed. Check your OpenAI API Key.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Network error. Make sure FastAPI is running.' });
    }
  };

  return (
    <div>
      <h1 className="page-title">AI Strategy Lab</h1>
      <p className="page-subtitle">Describe your trading logic in English, and the LLM will generate the raw Python code.</p>
      
      <div className="glass-panel">
        
        <div className="form-group">
          <label>Strategy Class Name (PascalCase)</label>
          <input 
            type="text" 
            className="input-field" 
            value={strategyName}
            onChange={(e) => setStrategyName(e.target.value)}
          />
        </div>
        
        <div className="form-group">
          <label>Strategy Logic</label>
          <textarea 
            className="input-field" 
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe when to BUY and when to SELL..."
          />
        </div>
        
        <button 
          className="btn-primary" 
          onClick={handleGenerate}
          disabled={status.type === 'loading' || !strategyName || !description}
        >
          <Cpu size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} />
          {status.type === 'loading' ? 'Generating Code...' : 'Generate Python Code'}
        </button>

        {status.message && (
          <div style={{ marginTop: '24px', padding: '16px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
            <div style={{ marginBottom: status.filePath ? '12px' : '0' }}>
              <span className={`status-badge ${status.type === 'success' ? 'status-success' : status.type === 'error' ? 'status-error' : ''}`}>
                {status.type === 'success' && <CheckCircle size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />}
                {status.type === 'error' && <AlertTriangle size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />}
                {status.message}
              </span>
            </div>
            
            {status.filePath && (
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                <Code size={16} />
                <span style={{ fontFamily: 'monospace' }}>Saved to: {status.filePath}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategyLabPage;
