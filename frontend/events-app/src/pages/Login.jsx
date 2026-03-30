import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const teal = '#005B5C';
const sand = '#E8D5B5';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handle = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch(err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ width: '100%', maxWidth: '400px', background: '#fff', border: '1px solid #e8e0d0', borderTop: `3px solid ${teal}`, borderRadius: '12px', padding: '40px 32px' }}>
        
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ width: '56px', height: '56px', background: teal, borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', fontSize: '24px', fontWeight: '800', color: sand }}>E</div>
          <h1 style={{ fontSize: '22px', fontWeight: '800', color: '#1a1a1a', margin: '0 0 6px' }}>WSM Events</h1>
          <p style={{ fontSize: '13px', color: '#888', margin: 0 }}>Sign in to manage your tournaments</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: '#555', marginBottom: '6px', letterSpacing: '0.5px' }}>EMAIL</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              style={{ width: '100%', padding: '12px 14px', border: '1px solid #e8e0d0', borderRadius: '8px', fontSize: '15px', outline: 'none', boxSizing: 'border-box', background: '#fafafa' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: '#555', marginBottom: '6px', letterSpacing: '0.5px' }}>PASSWORD</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{ width: '100%', padding: '12px 14px', border: '1px solid #e8e0d0', borderRadius: '8px', fontSize: '15px', outline: 'none', boxSizing: 'border-box', background: '#fafafa' }} />
          </div>

          {error && <div style={{ background: '#fff0f0', border: '1px solid #ffcdd2', color: '#c62828', padding: '10px 14px', borderRadius: '8px', fontSize: '13px' }}>{error}</div>}

          <button onClick={handle} disabled={loading}
            style={{ width: '100%', padding: '14px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: 'pointer', marginTop: '8px' }}>
            {loading ? 'Signing in...' : 'Sign in →'}
          </button>
        </div>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '12px', color: '#aaa' }}>
          {' '}
          <span onClick={() => navigate('/register')} style={{ color: teal, fontWeight: '600', cursor: 'pointer' }}>Create account →</span>
        </div>

        <div style={{ marginTop: '32px', paddingTop: '20px', borderTop: '1px solid #e8e0d0', textAlign: 'center', fontSize: '11px', color: '#ccc' }}>
          © 2026 World Strongman International Union
        </div>
      </div>
    </div>
  );
}
