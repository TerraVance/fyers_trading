import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink, CheckCircle, AlertTriangle } from 'lucide-react';

const BrokerPage = () => {
  const [loginUrl, setLoginUrl] = useState('');
  const [redirectUrl, setRedirectUrl] = useState('');
  const [status, setStatus] = useState<{type: 'idle' | 'loading' | 'success' | 'error', message: string}>({ type: 'idle', message: '' });
  const navigate = useNavigate();

  const fetchLoginUrl = async () => {
    setStatus({ type: 'loading', message: 'Fetching login URL...' });
    try {
      const res = await fetch('http://localhost:8000/api/v1/broker/login_url');
      const data = await res.json();
      setLoginUrl(data.login_url);
      setStatus({ type: 'idle', message: '' });
      window.open(data.login_url, '_blank');
    } catch (err) {
      setStatus({ type: 'error', message: 'Failed to fetch login URL. Is backend running?' });
    }
  };

  const submitAuth = async () => {
    if (!redirectUrl) return;
    
    // Extract auth_code from the pasted URL
    let authCode = redirectUrl;
    try {
      if (redirectUrl.includes('auth_code=')) {
        const urlObj = new URL(redirectUrl);
        authCode = urlObj.searchParams.get('auth_code') || redirectUrl;
      }
    } catch (e) {
      // If it's not a valid URL, maybe they just pasted the code directly
    }

    setStatus({ type: 'loading', message: 'Authenticating with Fyers...' });
    try {
      const res = await fetch('http://localhost:8000/api/v1/broker/submit_auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auth_code: authCode })
      });
      const data = await res.json();
      
      if (res.ok && data.success) {
        setStatus({ type: 'success', message: 'Successfully connected to Fyers API! Redirecting to Data Center...' });
        setTimeout(() => navigate('/data'), 1500);
      } else {
        setStatus({ type: 'error', message: data.message || 'Authentication failed' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Network error communicating with backend' });
    }
  };

  return (
    <div>
      <h1 className="page-title">Broker Connection</h1>
      <p className="page-subtitle">Authenticate your session with Fyers API for live trading.</p>
      
      <div className="glass-panel">
        <h3>Step 1: Generate Login Link</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
          Click the button below to open the Fyers login page in a new tab. Log in using your credentials.
        </p>
        <button className="btn-primary" onClick={fetchLoginUrl}>
          <ExternalLink size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} />
          Open Fyers Login
        </button>
      </div>

      <div className="glass-panel">
        <h3>Step 2: Submit Callback URL</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
          After logging in, you will be redirected to an empty page. Copy the full URL from your browser's address bar and paste it below.
        </p>
        
        <div className="form-group">
          <input 
            type="text" 
            className="input-field" 
            placeholder="https://localhost:8000/api/v1/broker/callback?s=ok&code=...&auth_code=XXXX"
            value={redirectUrl}
            onChange={(e) => setRedirectUrl(e.target.value)}
          />
        </div>
        
        <button 
          className="btn-primary" 
          onClick={submitAuth}
          disabled={!redirectUrl || status.type === 'loading'}
        >
          {status.type === 'loading' ? 'Authenticating...' : 'Submit Authentication'}
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

export default BrokerPage;
