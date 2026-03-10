import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';

export default function RefereeCompetitions() {
  const navigate = useNavigate();
  const [competitions, setCompetitions] = useState([]);
  const [divisions, setDivisions] = useState({});
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/competitions/').then(res => {
      setCompetitions(res.data);
    }).finally(() => setLoading(false));
  }, []);

  const loadDivisions = async (compId) => {
    if (expanded === compId) { setExpanded(null); return; }
    setExpanded(compId);
    if (divisions[compId]) return;
    const res = await api.get(`/competition/${compId}`);
    setDivisions(d => ({ ...d, [compId]: res.data }));
  };

  return (
    <Layout>
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>Referee Portal</h1>
        <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>Select competition and division to enter results</p>
      </div>

      {loading && <p style={{ color: '#555' }}>Loading...</p>}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {competitions.map(c => (
          <div key={c.id}>
            <div
              onClick={() => loadDivisions(c.id)}
              style={{ background: '#111', border: `1px solid ${expanded === c.id ? gold : '#1e1e1e'}`, borderRadius: '4px', padding: '16px 24px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              onMouseEnter={e => e.currentTarget.style.borderColor = gold}
              onMouseLeave={e => e.currentTarget.style.borderColor = expanded === c.id ? gold : '#1e1e1e'}
            >
              <div>
                <div style={{ color: '#fff', fontWeight: '600', fontSize: '15px' }}>{c.name}</div>
                <div style={{ color: '#555', fontSize: '12px', marginTop: '2px' }}>
                  {c.date_start || 'No date'}{c.city ? ` · ${c.city}` : ''}{c.country ? `, ${c.country}` : ''}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ background: 'rgba(201,168,76,0.1)', color: gold, fontSize: '11px', fontWeight: '700', padding: '3px 8px', borderRadius: '2px' }}>Q {c.coefficient_q}</div>
                <span style={{ color: gold, fontSize: '16px' }}>{expanded === c.id ? '▲' : '▼'}</span>
              </div>
            </div>

            {expanded === c.id && (
              <div style={{ borderLeft: `2px solid ${gold}`, marginLeft: '24px', paddingLeft: '16px', marginTop: '4px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {!divisions[c.id] && <p style={{ color: '#555', padding: '12px 0', fontSize: '13px' }}>Loading divisions...</p>}
                {divisions[c.id]?.map(div => (
                  <div
                    key={div.id}
                    onClick={() => navigate(`/referee/${div.id}/disciplines`)}
                    style={{ background: '#0d0d0d', border: '1px solid #1a1a1a', borderRadius: '3px', padding: '12px 20px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = gold}
                    onMouseLeave={e => e.currentTarget.style.borderColor = '#1a1a1a'}
                  >
                    <div>
                      <span style={{ color: '#fff', fontWeight: '600' }}>{div.division_key}</span>
                      {div.age_group && <span style={{ color: '#666', fontSize: '12px', marginLeft: '8px' }}>{div.age_group}</span>}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '10px', letterSpacing: '1px', padding: '2px 8px', border: '1px solid', borderRadius: '2px', color: div.status === 'LIVE' ? '#7a9a7a' : div.status === 'LOCKED' ? gold : '#444', borderColor: div.status === 'LIVE' ? '#7a9a7a' : div.status === 'LOCKED' ? gold : '#333' }}>
                        {div.status}
                      </span>
                      <span style={{ color: '#333' }}>→</span>
                    </div>
                  </div>
                ))}
                {divisions[c.id]?.length === 0 && <p style={{ color: '#444', padding: '12px 0', fontSize: '13px' }}>No divisions</p>}
              </div>
            )}
          </div>
        ))}
      </div>
    </Layout>
  );
}
