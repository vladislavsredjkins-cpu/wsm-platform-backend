import { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import api from '../api';

const gold = '#c9a84c';

export default function Divisions({ competition, onBack, onSelect }) {
  const [divisions, setDivisions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/divisions/competition/${competition.id}`)
      .then(res => setDivisions(res.data))
      .finally(() => setLoading(false));
  }, [competition.id]);

  return (
    <div style={{ background: '#0a0a0a', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      {/* Header */}
      <div style={{ background: '#111', borderBottom: '1px solid #1e1e1e', padding: '0 32px', display: 'flex', alignItems: 'center', height: '60px', gap: '12px' }}>
        <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" alt="WSM" style={{ height: '32px' }} />
        <span style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px' }}>REFEREE PORTAL</span>
      </div>

      <div style={{ padding: '40px 32px' }}>
        {/* Breadcrumb */}
        <div style={{ marginBottom: '24px' }}>
          <button onClick={onBack} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', fontSize: '13px', padding: 0 }}>
            ← Competitions
          </button>
        </div>

        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>{competition.name}</h1>
          <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>Select a division</p>
        </div>

        {loading && <p style={{ color: '#555' }}>Loading...</p>}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {divisions.map(d => (
            <div key={d.id}
              onClick={() => onSelect(d)}
              style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
              onMouseEnter={e => e.currentTarget.style.borderColor = gold}
              onMouseLeave={e => e.currentTarget.style.borderColor = '#1e1e1e'}
            >
              <div>
                <div style={{ color: '#fff', fontWeight: '600', fontSize: '16px', marginBottom: '4px' }}>{d.division_key}</div>
                <div style={{ color: '#555', fontSize: '12px' }}>{d.format} · {d.status} {d.is_locked ? '🔒' : ''}</div>
              </div>
              <span style={{ color: '#444', fontSize: '18px' }}>→</span>
            </div>
          ))}
          {!loading && divisions.length === 0 && (
            <p style={{ color: '#444' }}>No divisions found.</p>
          )}
        </div>
      </div>
    </div>
  );
}
