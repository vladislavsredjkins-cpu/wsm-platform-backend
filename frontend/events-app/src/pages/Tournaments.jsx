import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const teal = '#005B5C';
const sand = '#E8D5B5';
const API = 'https://api.events.worldstrongman.org';

const SPORTS = ['All', 'Strongman', 'Strict Curl', 'Stick Pulling', 'Powerlifting'];

export default function Tournaments() {
  const navigate = useNavigate();
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sport, setSport] = useState('All');

  useEffect(() => {
    axios.get(`${API}/events-api/tournaments/all`)
      .then(r => setCompetitions(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = sport === 'All' ? competitions : competitions.filter(c =>
    c.sport_type === sport.toLowerCase().replace(' ', '_') ||
    c.name.toLowerCase().includes(sport.toLowerCase())
  );

  if (loading) return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ color: '#888' }}>Loading tournaments...</div>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef' }}>
      {/* Header */}
      <div style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '16px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => navigate('/')}>
          <div style={{ width: '36px', height: '36px', background: teal, borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', fontWeight: '800', color: sand }}>W</div>
          <span style={{ fontWeight: '700', color: '#1a1a1a', fontSize: '15px' }}>WSM Events</span>
        </div>
        <button onClick={() => navigate('/login')}
          style={{ padding: '8px 16px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>
          Organizer Login
        </button>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '40px 24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '800', color: '#1a1a1a', margin: '0 0 8px' }}>Upcoming Tournaments</h1>
        <p style={{ color: '#888', fontSize: '14px', margin: '0 0 24px' }}>Register for upcoming competitions worldwide</p>

        {/* Sport filter */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '32px' }}>
          {SPORTS.map(s => (
            <button key={s} onClick={() => setSport(s)}
              style={{ padding: '7px 16px', border: sport === s ? 'none' : '1px solid #e8e0d0', borderRadius: '20px', fontSize: '13px', fontWeight: '600', cursor: 'pointer', background: sport === s ? teal : '#fff', color: sport === s ? '#fff' : '#666' }}>
              {s}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: '#aaa' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏆</div>
            <p>No tournaments found.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))', gap: '20px' }}>
            {filtered.map(c => (
              <div key={c.id} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                {c.banner_url ? (
                  <img src={c.banner_url} alt={c.name} style={{ width: '100%', height: '180px', objectFit: 'cover' }} />
                ) : (
                  <div style={{ width: '100%', height: '100px', background: `linear-gradient(135deg, ${teal}, #007a7b)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <span style={{ fontSize: '36px' }}>🏆</span>
                  </div>
                )}
                <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px', marginBottom: '10px' }}>
                    <h2 style={{ fontSize: '17px', fontWeight: '800', color: '#1a1a1a', margin: 0, lineHeight: '1.3' }}>{c.name}</h2>
                    {c.status === 'DRAFT' && (
                      <span style={{ fontSize: '10px', fontWeight: '700', background: '#fff3e0', color: '#e07b00', padding: '2px 7px', borderRadius: '4px', whiteSpace: 'nowrap' }}>DRAFT</span>
                    )}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '12px' }}>
                    <span style={{ fontSize: '13px', color: '#666' }}>📅 {c.date_start}{c.date_end && c.date_end !== c.date_start ? ` — ${c.date_end}` : ''}</span>
                    <span style={{ fontSize: '13px', color: '#666' }}>📍 {c.city}, {c.country}</span>
                    {c.entry_fee_enabled && c.entry_fee && (
                      <span style={{ fontSize: '13px', color: teal, fontWeight: '600' }}>💳 Entry fee: €{c.entry_fee}</span>
                    )}
                    {c.registration_deadline && (
                      <span style={{ fontSize: '12px', color: '#e07b00', fontWeight: '600' }}>⏰ Deadline: {c.registration_deadline}</span>
                    )}
                  </div>
                  {c.description && (
                    <p style={{ fontSize: '12px', color: '#999', margin: '0 0 12px', lineHeight: '1.5', flexGrow: 1 }}>{c.description}</p>
                  )}
                  <button onClick={() => navigate(`/tournament/${c.id}/register`)}
                    style={{ width: '100%', padding: '11px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: '700', cursor: 'pointer', marginTop: 'auto' }}>
                    Register →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
