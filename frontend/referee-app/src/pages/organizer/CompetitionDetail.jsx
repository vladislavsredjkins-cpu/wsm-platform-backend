import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';
const labelStyle = { display: 'block', color: '#888', fontSize: '11px', fontWeight: '600', letterSpacing: '1px', marginBottom: '6px' };
const inputStyle = { width: '100%', padding: '11px 14px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '14px', outline: 'none', boxSizing: 'border-box' };

const TABS = ['Divisions', 'Athletes', 'Disciplines'];

export default function CompetitionDetail() {
  const { competitionId } = useParams();
  const navigate = useNavigate();
  const [competition, setCompetition] = useState(null);
  const [divisions, setDivisions] = useState([]);
  const [tab, setTab] = useState('Divisions');
  const [loading, setLoading] = useState(true);

  // Division form
  const [showDivForm, setShowDivForm] = useState(false);
  const [divForm, setDivForm] = useState({ division_key: '', format: 'CLASSIC' });
  const [savingDiv, setSavingDiv] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get(`/competitions/${competitionId}`),
      api.get(`/divisions/competition/${competitionId}`),
    ]).then(([compRes, divRes]) => {
      setCompetition(compRes.data);
      setDivisions(divRes.data);
    }).finally(() => setLoading(false));
  }, [competitionId]);

  const createDivision = async () => {
    if (!divForm.division_key) return alert('Division key required');
    setSavingDiv(true);
    try {
      const res = await api.post('/divisions/', {
        competition_id: competitionId,
        division_key: divForm.division_key,
        format: divForm.format,
      });
      setDivisions(d => [...d, res.data]);
      setShowDivForm(false);
      setDivForm({ division_key: '', format: 'CLASSIC' });
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to create division');
    } finally {
      setSavingDiv(false);
    }
  };

  if (loading) return <Layout><p style={{ color: '#555' }}>Loading...</p></Layout>;
  if (!competition) return <Layout><p style={{ color: '#555' }}>Competition not found</p></Layout>;

  return (
    <Layout>
      {/* Breadcrumb */}
      <div style={{ marginBottom: '20px', fontSize: '13px', color: '#555', display: 'flex', gap: '8px' }}>
        <button onClick={() => navigate('/organizer/competitions')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>Competitions</button>
        <span>›</span>
        <span style={{ color: '#888' }}>{competition.name}</span>
      </div>

      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h1 style={{ color: '#fff', fontSize: '24px', fontWeight: '700', margin: '0 0 6px' }}>{competition.name}</h1>
            <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>
              {competition.date_start || 'No date'}
              {competition.city ? ` · ${competition.city}` : ''}
              {competition.country ? ` · ${competition.country}` : ''}
            </p>
          </div>
          <div style={{ background: 'rgba(201,168,76,0.1)', color: gold, fontSize: '13px', fontWeight: '700', padding: '8px 16px', borderRadius: '3px', border: `1px solid rgba(201,168,76,0.3)` }}>
            Q {competition.coefficient_q}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '24px', borderBottom: '1px solid #1e1e1e', paddingBottom: '0' }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            background: 'none', border: 'none', color: tab === t ? gold : '#555',
            padding: '10px 20px', cursor: 'pointer', fontSize: '13px', fontWeight: tab === t ? '700' : '400',
            borderBottom: tab === t ? `2px solid ${gold}` : '2px solid transparent',
            marginBottom: '-1px',
          }}>
            {t}
          </button>
        ))}
      </div>

      {/* DIVISIONS TAB */}
      {tab === 'Divisions' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
            <button onClick={() => setShowDivForm(!showDivForm)} style={{ padding: '8px 20px', background: showDivForm ? 'transparent' : gold, color: showDivForm ? gold : '#000', border: `1px solid ${gold}`, borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
              {showDivForm ? 'CANCEL' : '+ ADD DIVISION'}
            </button>
          </div>

          {showDivForm && (
            <div style={{ background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '20px', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={labelStyle}>Division Key</label>
                  <select style={inputStyle} value={divForm.division_key} onChange={e => setDivForm(f => ({ ...f, division_key: e.target.value }))}>
                    <option value="">Select division</option>
                    <option value="MEN">MEN</option>
                    <option value="WOMEN">WOMEN</option>
                    
                    
                    
                    
                    <option value="PARA">PARA</option>
                    
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>Format</label>
                  <select style={inputStyle} value={divForm.format} onChange={e => setDivForm(f => ({ ...f, format: e.target.value }))}>
                    <option value="CLASSIC">Classic</option>
                    <option value="RELAY">Relay</option><option value="TEAM_BATTLE">Team Battle</option>
                    
                  </select>
                </div>
              </div>
              <button onClick={createDivision} disabled={savingDiv} style={{ marginTop: '16px', padding: '10px 28px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
                {savingDiv ? 'CREATING...' : 'CREATE DIVISION →'}
              </button>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {divisions.map(d => (
              <div key={d.id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '18px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                onMouseEnter={e => e.currentTarget.style.borderColor = gold}
                onMouseLeave={e => e.currentTarget.style.borderColor = '#1e1e1e'}
              >
                <div>
                  <div style={{ color: '#fff', fontWeight: '600', fontSize: '15px', marginBottom: '3px' }}>{d.division_key}</div>
                  <div style={{ color: '#555', fontSize: '12px' }}>{d.format} · {d.status}</div>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <StatusBadge status={d.status} />
                </div>
              </div>
            ))}
            {divisions.length === 0 && <p style={{ color: '#444' }}>No divisions yet. Add one above.</p>}
          </div>
        </div>
      )}

      {/* ATHLETES TAB */}
      {tab === 'Athletes' && (
        <div>
          <p style={{ color: '#555' }}>Athletes registration — coming soon</p>
        </div>
      )}

      {/* DISCIPLINES TAB */}
      {tab === 'Disciplines' && (
        <div>
          <p style={{ color: '#555' }}>Disciplines management — coming soon</p>
        </div>
      )}
    </Layout>
  );
}

function StatusBadge({ status }) {
  const colors = {
    OPEN: { bg: 'rgba(76,175,80,0.1)', color: '#4caf50' },
    LOCKED: { bg: 'rgba(255,152,0,0.1)', color: '#ff9800' },
    DRAFT: { bg: 'rgba(100,100,100,0.1)', color: '#888' },
  };
  const style = colors[status] || colors.DRAFT;
  return (
    <div style={{ background: style.bg, color: style.color, fontSize: '11px', fontWeight: '700', padding: '3px 10px', borderRadius: '2px' }}>
      {status}
    </div>
  );
}
