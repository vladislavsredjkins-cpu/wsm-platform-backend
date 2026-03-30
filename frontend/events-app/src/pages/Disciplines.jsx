import { useEffect, useState } from 'react';
import api from '../api';

const gold = '#c9a84c';

export default function Disciplines({ competition, division, onBack, onSelect }) {
  const [disciplines, setDisciplines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/disciplines/division/${division.id}`)
      .then(res => setDisciplines(res.data))
      .finally(() => setLoading(false));
  }, [division.id]);

  return (
    <div style={{ background: '#0a0a0a', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ background: '#111', borderBottom: '1px solid #1e1e1e', padding: '0 32px', display: 'flex', alignItems: 'center', height: '60px', gap: '12px' }}>
        <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" alt="WSM" style={{ height: '32px' }} />
        <span style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px' }}>REFEREE PORTAL</span>
      </div>

      <div style={{ padding: '40px 32px' }}>
        <div style={{ marginBottom: '24px', display: 'flex', gap: '8px', color: '#555', fontSize: '13px' }}>
          <button onClick={() => onBack('competitions')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>Competitions</button>
          <span>›</span>
          <button onClick={() => onBack('divisions')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>{competition.name}</button>
          <span>›</span>
          <span style={{ color: '#888' }}>{division.division_key}</span>
        </div>

        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>{division.division_key}</h1>
          <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>Select a discipline to enter results</p>
        </div>

        {loading && <p style={{ color: '#555' }}>Loading...</p>}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {disciplines.map((d, i) => (
            <div key={d.id}
              onClick={() => onSelect(d)}
              style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
              onMouseEnter={e => e.currentTarget.style.borderColor = gold}
              onMouseLeave={e => e.currentTarget.style.borderColor = '#1e1e1e'}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ color: gold, fontSize: '12px', fontWeight: '700', width: '24px' }}>#{d.order_no || i + 1}</div>
                <div>
                  <div style={{ color: '#fff', fontWeight: '600', fontSize: '16px', marginBottom: '4px' }}>{d.discipline_name}</div>
                  <div style={{ color: '#555', fontSize: '12px' }}>{d.discipline_mode || 'Standard'}{d.time_cap_seconds ? ` · ${d.time_cap_seconds}s cap` : ''}</div>
                </div>
              </div>
              <span style={{ color: '#444', fontSize: '18px' }}>→</span>
            </div>
          ))}
          {!loading && disciplines.length === 0 && (
            <p style={{ color: '#444' }}>No disciplines found.</p>
          )}
        </div>
      </div>
    </div>
  );
}
