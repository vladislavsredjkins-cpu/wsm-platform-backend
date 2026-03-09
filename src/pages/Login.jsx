import { useState } from 'react';
import { useAuth } from '../AuthContext';

export default function Login({ onSuccess }) {
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
      onSuccess?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.header}>
          <img
            src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png"
            alt="WSM"
            style={styles.logo}
          />
          <div style={styles.tag}>REFEREE PORTAL</div>
          <h1 style={styles.title}>Sign In</h1>
          <p style={styles.sub}>World Strongman Competition System</p>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input
              style={styles.input}
              type="email"
              placeholder="referee@wsm.org"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              style={styles.input}
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div style={styles.error}>{error}</div>}
          <button style={styles.btn} type="submit" disabled={loading}>
            {loading ? 'SIGNING IN...' : 'SIGN IN →'}
          </button>
        </form>

        <div style={styles.footer}>
          © {new Date().getFullYear()} World Strongman International Union
        </div>
      </div>
    </div>
  );
}

const gold = '#c9a84c';

const styles = {
  page: {
    minHeight: '100vh',
    background: '#0a0a0a',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontFamily: "'Segoe UI', system-ui, sans-serif",
  },
  card: {
    width: '420px',
    background: '#111',
    border: '1px solid #1e1e1e',
    borderTop: `3px solid ${gold}`,
    borderRadius: '4px',
    padding: '48px 40px 32px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '36px',
  },
  logo: {
    width: '80px',
    marginBottom: '16px',
  },
  tag: {
    display: 'inline-block',
    background: 'rgba(201,168,76,0.1)',
    color: gold,
    fontSize: '10px',
    fontWeight: '700',
    letterSpacing: '3px',
    padding: '4px 12px',
    borderRadius: '2px',
    border: `1px solid rgba(201,168,76,0.3)`,
    marginBottom: '16px',
  },
  title: {
    color: '#fff',
    fontSize: '26px',
    fontWeight: '700',
    margin: '0 0 6px',
  },
  sub: {
    color: '#555',
    fontSize: '13px',
    margin: 0,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    color: '#888',
    fontSize: '11px',
    fontWeight: '600',
    letterSpacing: '1px',
    textTransform: 'uppercase',
  },
  input: {
    padding: '13px 14px',
    background: '#0a0a0a',
    border: '1px solid #2a2a2a',
    borderRadius: '3px',
    color: '#fff',
    fontSize: '15px',
    outline: 'none',
  },
  btn: {
    marginTop: '8px',
    padding: '14px',
    background: gold,
    color: '#000',
    border: 'none',
    borderRadius: '3px',
    fontSize: '12px',
    fontWeight: '700',
    letterSpacing: '2px',
    cursor: 'pointer',
  },
  error: {
    background: 'rgba(220,53,69,0.1)',
    border: '1px solid rgba(220,53,69,0.3)',
    color: '#dc3545',
    padding: '10px 14px',
    borderRadius: '3px',
    fontSize: '13px',
  },
  footer: {
    marginTop: '32px',
    textAlign: 'center',
    color: '#333',
    fontSize: '11px',
  },
};