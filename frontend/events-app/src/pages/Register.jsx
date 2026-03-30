import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const teal = '#005B5C';
const sand = '#E8D5B5';
const API = 'https://api.events.worldstrongman.org';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '', confirm: '', name: '', country: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handle = async () => {
    setError('');
    if (!form.email || !form.password || !form.name) { setError('Please fill all required fields'); return; }
    if (form.password !== form.confirm) { setError('Passwords do not match'); return; }
    if (form.password.length < 6) { setError('Password must be at least 6 characters'); return; }
    setLoading(true);
    try {
      const res = await axios.post(`${API}/auth/register`, {
        email: form.email,
        password: form.password,
        name: form.name,
        country: form.country,
        type: 'club',
      });
      const { access_token, role, organizer_id } = res.data;
      localStorage.setItem('token', access_token);
      const user = { email: form.email, role, organizer_id };
      localStorage.setItem('user', JSON.stringify(user));
      navigate('/dashboard');
    } catch(e) {
      setError(e.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const inp = { width: '100%', padding: '12px 14px', border: '1px solid #e8e0d0', borderRadius: '8px', fontSize: '15px', outline: 'none', boxSizing: 'border-box', background: '#fafafa' };
  const lbl = { display: 'block', fontSize: '12px', fontWeight: '600', color: '#555', marginBottom: '6px', letterSpacing: '0.5px' };

  return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ width: '100%', maxWidth: '420px', background: '#fff', border: '1px solid #e8e0d0', borderTop: `3px solid ${teal}`, borderRadius: '12px', padding: '40px 32px' }}>

        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ width: '56px', height: '56px', background: teal, borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', fontSize: '24px', fontWeight: '800', color: sand }}>E</div>
          <h1 style={{ fontSize: '22px', fontWeight: '800', color: '#1a1a1a', margin: '0 0 6px' }}>Create account</h1>
          <p style={{ fontSize: '13px', color: '#888', margin: 0 }}>Start organizing tournaments today</p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={lbl}>ORGANIZATION NAME *</label>
            <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="e.g. Latvia Strongman Federation" style={inp} />
          </div>
          <div>
            <label style={lbl}>EMAIL *</label>
            <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="you@example.com" style={inp} />
          </div>
          <div>
            <label style={lbl}>COUNTRY</label>
            <input value={form.country} onChange={e => setForm({...form, country: e.target.value})} placeholder="e.g. Latvia" style={inp} />
          </div>
          <div>
            <label style={lbl}>PASSWORD *</label>
            <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} placeholder="Min 6 characters" style={inp} />
          </div>
          <div>
            <label style={lbl}>CONFIRM PASSWORD *</label>
            <input type="password" value={form.confirm} onChange={e => setForm({...form, confirm: e.target.value})} placeholder="Repeat password" style={inp} />
          </div>

          {error && <div style={{ background: '#fff0f0', border: '1px solid #ffcdd2', color: '#c62828', padding: '10px 14px', borderRadius: '8px', fontSize: '13px' }}>{error}</div>}

          <button onClick={handle} disabled={loading}
            style={{ width: '100%', padding: '14px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: 'pointer', marginTop: '8px' }}>
            {loading ? 'Creating account...' : 'Create account →'}
          </button>

          <p style={{ fontSize: '11px', color: '#aaa', textAlign: 'center', margin: 0 }}>
            By registering you agree to our{' '}
            <a href="https://worldstrongman.org/privacy-policy" target="_blank" style={{ color: teal }}>Privacy Policy</a>
          </p>
        </div>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '13px', color: '#888' }}>
          Already have an account?{' '}
          <span onClick={() => navigate('/login')} style={{ color: teal, fontWeight: '600', cursor: 'pointer' }}>Sign in</span>
        </div>

        <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #e8e0d0', textAlign: 'center', fontSize: '11px', color: '#ccc' }}>
          © 2026 World Strongman International Union
        </div>
      </div>
    </div>
  );
}
