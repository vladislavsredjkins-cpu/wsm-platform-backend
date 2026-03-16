import { useAuth } from '../../AuthContext';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';

export default function ASLDashboard() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'WSM_ADMIN';
  const navigate = useNavigate();
  const [leagues, setLeagues] = useState([]);
  const [divisions, setDivisions] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', season: '2026' });

  useEffect(() => {
    api.get('/api/asl/leagues').then(r => {
      setLeagues(r.data);
      if (r.data.length > 0) selectLeague(r.data[0]);
    }).finally(() => setLoading(false));
  }, []);

  const selectLeague = (league) => {
    setSelectedLeague(league);
    api.get(`/api/asl/divisions?league_id=${league.id}`).then(r => setDivisions(r.data));
  };

  const createLeague = async () => {
    const res = await api.post('/api/asl/leagues', form);
    setLeagues([...leagues, res.data]);
    selectLeague(res.data);
    setShowForm(false);
  };

  return (
    <Layout>
      <div style={{ marginBottom: '28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ color: gold, fontSize: '11px', letterSpacing: '3px', marginBottom: '6px' }}>ASL LEAGUE</div>
          <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: 0 }}>League Management</h1>
        </div>
        {isAdmin && <button onClick={() => setShowForm(!showForm)} style={{ padding: '10px 20px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>+ NEW LEAGUE</button>}
      </div>

      {showForm && (
        <div style={{ background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '20px', marginBottom: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
            <div>
              <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '6px' }}>LEAGUE NAME</label>
              <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="ASL Season 2026"
                style={{ width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }} />
            </div>
            <div>
              <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '6px' }}>SEASON</label>
              <input value={form.season} onChange={e => setForm({...form, season: e.target.value})} placeholder="2026"
                style={{ width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }} />
            </div>
          </div>
          <button onClick={createLeague} style={{ padding: '10px 24px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
            CREATE →
          </button>
        </div>
      )}

      {/* Leagues tabs */}
      {leagues.length > 0 && (
        <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #1e1e1e', paddingBottom: '0' }}>
          {leagues.map(l => (
            <button key={l.id} onClick={() => selectLeague(l)}
              style={{ padding: '10px 20px', background: 'none', border: 'none', color: selectedLeague?.id === l.id ? gold : '#555', fontSize: '13px', fontWeight: selectedLeague?.id === l.id ? '700' : '400', cursor: 'pointer', borderBottom: selectedLeague?.id === l.id ? `2px solid ${gold}` : '2px solid transparent' }}>
              {l.name}
            </button>
          ))}
        </div>
      )}

      {/* Divisions */}
      {selectedLeague && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ color: '#888', fontSize: '11px', letterSpacing: '2px' }}>DIVISIONS</div>
            <button onClick={() => navigate(`/asl/leagues/${selectedLeague.id}/divisions/new`)}
              style={{ padding: '6px 14px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>
              {isAdmin ? '+ ADD DIVISION' : ''}
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {divisions.map(d => (
              <div key={d.id} onClick={() => navigate(`/asl/divisions/${d.id}`)}
                style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '16px 20px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                onMouseEnter={e => e.currentTarget.style.borderColor = gold}
                onMouseLeave={e => e.currentTarget.style.borderColor = '#1e1e1e'}>
                <div>
                  <div style={{ color: '#fff', fontWeight: '600', fontSize: '15px' }}>{d.name}</div>
                  <div style={{ color: '#555', fontSize: '12px', marginTop: '2px' }}>{d.region || 'No region'} · Max {d.max_teams} teams</div>
                </div>
                <span style={{ color: '#333' }}>→</span>
              </div>
            ))}
            {divisions.length === 0 && <p style={{ color: '#444', fontSize: '13px' }}>No divisions yet.</p>}
          </div>
        </div>
      )}
    </Layout>
  );
}
