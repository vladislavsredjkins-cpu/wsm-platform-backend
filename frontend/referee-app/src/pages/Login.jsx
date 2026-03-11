import { useState } from 'react';
import { useAuth } from '../AuthContext';

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const gold = '#c9a84c';
  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0a', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui, sans-serif', padding: '16px', boxSizing: 'border-box', overflowX: 'hidden', width: '100%' }}>
      <div style={{ width: '100%', maxWidth: '400px', boxSizing: 'border-box', background: '#111', border: '1px solid #1e1e1e', borderTop: '3px solid ' + gold, borderRadius: '4px', padding: '40px 24px 28px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" alt="WSM" style={{ width: '72px', display: 'block', margin: '0 auto 14px' }} />
          <div style={{ display: 'inline-block', background: 'rgba(201,168,76,0.1)', color: gold, fontSize: '10px', fontWeight: '700', letterSpacing: '3px', padding: '4px 12px', border: '1px solid rgba(201,168,76,0.3)', marginBottom: '14px' }}>
            REFEREE PORTAL
          </div>
          <h1 style={{ color: '#fff', fontSize: '24px', fontWeight: '700', margin: '0 0 6px' }}>Sign In</h1>
          <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>World Strongman Competition System</p>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ color: '#888', fontSize: '11px', fontWeight: '600', letterSpacing: '1px' }}>EMAIL</label>
            <input type="email" placeholder="referee@wsm.org" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ padding: '13px 14px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '15px', outline: 'none', width: '100%', boxSizing: 'border-box' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ color: '#888', fontSize: '11px', fontWeight: '600', letterSpacing: '1px' }}>PASSWORD</label>
            <input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ padding: '13px 14px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '15px', outline: 'none', width: '100%', boxSizing: 'border-box' }} />
          </div>
          {error && <div style={{ background: 'rgba(220,53,69,0.1)', border: '1px solid rgba(220,53,69,0.3)', color: '#dc3545', padding: '10px 14px', borderRadius: '3px', fontSize: '13px' }}>{error}</div>}
          <button type="button" disabled={loading} onClick={handleSubmit} style={{ marginTop: '8px', padding: '14px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', letterSpacing: '2px', cursor: 'pointer', width: '100%', boxSizing: 'border-box' }}>
            {loading ? 'SIGNING IN...' : 'SIGN IN →'}
          </button>
        </div>
        <div style={{ marginTop: '28px', textAlign: 'center', color: '#333', fontSize: '11px' }}>
          © {new Date().getFullYear()} World Strongman International Union
        </div>
      </div>
    </div>
  );
}
