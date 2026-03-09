import { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import { getCompetitions } from '../api';

const gold = '#c9a84c';

export default function Dashboard({ onSelect }) {
  const { user, logout } = useAuth();
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getCompetitions()
      .then(res => setCompetitions(res.data))
      .catch(() => setError('Failed to load competitions'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ background: '#0a0a0a', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      {/* Header */}
      <div style={{ background: '#111', borderBottom: '1px solid #1e1e1e', padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '60px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" alt="WSM" style={{ height: '32px' }} />
          <span style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px' }}>REFEREE PORTAL</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#555', fontSize: '13px' }}>{user?.email}</span>
          <button onClick={logout} style={{ background: 'transparent', border: '1px solid #333', color: '#888', padding: '6px 14px', borderRadius: '3px', cursor: 'pointer', fontSize: '12px' }}>
            Logout
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '40px 32px' }}>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>Competitions</h1>
          <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>Select a competition to enter results</p>
        </div>

        {loading && <p style={{ color: '#555' }}>Loading...</p>}
        {error && <p style={{ color: '#dc3545' }}>{error}</p>}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {competitions.map(c => (
            <div key={c.id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', transition: 'border-color 0.2s' }}
              onClick={() => onSelect(c)}
              onMouseEnter={e => e.currentTarget.style.borderColor = gold}
              onMouseLeave={e => e.currentTarget.style.borderColor = '#1e1e1e'}
            >
              <div>
                <div style={{ color: '#fff', fontWeight: '600', fontSize: '16px', marginBottom: '4px' }}>{c.name}</div>
                <div style={{ color: '#555', fontSize: '12px' }}>
                  {c.date_start || 'No date'} {c.city ? `· ${c.city}` : ''} {c.country ? `· ${c.country}` : ''}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ background: 'rgba(201,168,76,0.1)', color: gold, fontSize: '11px', fontWeight: '700', padding: '4px 10px', borderRadius: '2px' }}>
                  Q {c.coefficient_q}
                </div>
                <span style={{ color: '#444', fontSize: '18px' }}>→</span>
              </div>
            </div>
          ))}
          {!loading && competitions.length === 0 && (
            <p style={{ color: '#444', fontSize: '14px' }}>No competitions found.</p>
          )}
        </div>
      </div>
    </div>
  );
}
