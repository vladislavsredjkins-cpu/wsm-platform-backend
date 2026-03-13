import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';
const STANDARD_DISCIPLINES = [
  { name: 'Stone Flip',             unit: 'reps', result_type: 'higher_wins' },
  { name: 'Dumbbell Lift',          unit: 'reps', result_type: 'higher_wins' },
  { name: 'Axle Deadlift',          unit: 'reps', result_type: 'higher_wins' },
  { name: 'Log Lift',               unit: 'reps', result_type: 'higher_wins' },
  { name: 'Husafell Sandbag Carry', unit: 'sec',  result_type: 'lower_wins'  },
  { name: 'Super Yoke',             unit: 'sec',  result_type: 'lower_wins'  },
  { name: "Farmer's Walk",          unit: 'sec',  result_type: 'lower_wins'  },
  { name: 'Tire Flips',             unit: 'sec',  result_type: 'lower_wins'  },
];

export default function ASLDivision() {
  const { divisionId } = useParams();
  const navigate = useNavigate();
  const [division, setDivision] = useState(null);
  const [teams, setTeams] = useState([]);
  const [standings, setStandings] = useState([]);
  const [matches, setMatches] = useState([]);
  const [allTeams, setAllTeams] = useState([]);
  const [tab, setTab] = useState('Standings');
  const [showMatchForm, setShowMatchForm] = useState(false);
  const [matchForm, setMatchForm] = useState({ home_team_id: '', away_team_id: '', match_date: '', round_number: 1, judge_id: '', judge2_id: '' });
  const [showAddTeam, setShowAddTeam] = useState(false);
  const [judges, setJudges] = useState([]);
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [selectedDisciplines, setSelectedDisciplines] = useState([]);
  const [editResult, setEditResult] = useState(null);
  const [resultForm, setResultForm] = useState({ home_score: 0, away_score: 0 });

  useEffect(() => {
    api.get(`/api/asl/divisions/${divisionId}/detail`).then(r => setDivision(r.data));
    Promise.all([
      api.get(`/api/asl/divisions/${divisionId}/teams`).then(r => setTeams(r.data)),
      api.get(`/api/asl/divisions/${divisionId}/standings`).then(r => setStandings(r.data)),
      api.get(`/api/asl/divisions/${divisionId}/matches`).then(r => setMatches(r.data)),
      api.get('/teams/').then(r => setAllTeams(r.data)),
      api.get('/judges/').then(r => setJudges(r.data)).catch(() => {}),
    ]);
  }, [divisionId]);

  const addTeam = async () => {
    await api.post(`/api/asl/divisions/${divisionId}/teams`, { team_id: selectedTeamId });
    const res = await api.get(`/api/asl/divisions/${divisionId}/teams`);
    setTeams(res.data);
    setShowAddTeam(false);
  };

  const createMatch = async () => {
    if (selectedDisciplines.length !== 5) {
      alert('Please select exactly 5 disciplines');
      return;
    }
    const res1 = await api.post('/api/asl/matches', { ...matchForm, asl_division_id: divisionId, round_number: parseInt(matchForm.round_number) });
    const matchId = res1.data.id;
    for (const d of selectedDisciplines) {
      await api.post(`/api/asl/matches/${matchId}/disciplines`, { discipline_name: d.name, result_type: d.result_type, unit: d.unit, home_result: 0, away_result: 0 });
    }
    const res = await api.get(`/api/asl/divisions/${divisionId}/matches`);
    setMatches(res.data);
    setShowMatchForm(false);
    setSelectedDisciplines([]);
  };

  const deleteMatch = async (matchId) => {
    if (!confirm('Delete this match?')) return;
    await api.delete(`/api/asl/matches/${matchId}`);
    const res = await api.get(`/api/asl/divisions/${divisionId}/matches`);
    setMatches(res.data);
  };

  const saveResult = async () => {
    await api.patch(`/api/asl/matches/${editResult}/result`, resultForm);
    const [m, s] = await Promise.all([
      api.get(`/api/asl/divisions/${divisionId}/matches`),
      api.get(`/api/asl/divisions/${divisionId}/standings`),
    ]);
    setMatches(m.data);
    setStandings(s.data);
    setEditResult(null);
  };

  const getTeamName = (id) => teams.find(t => t.id === id)?.name || allTeams.find(t => t.id === id)?.name || '—';

  return (
    <Layout>
      <div style={{ marginBottom: '24px' }}>
        <div style={{ color: '#555', fontSize: '12px', marginBottom: '8px', cursor: 'pointer' }} onClick={() => navigate('/asl')}>← ASL League</div>
        <div style={{ color: gold, fontSize: '11px', letterSpacing: '3px', marginBottom: '6px' }}>DIVISION</div>
        <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: 0 }}>{division?.name || 'Loading...'}</h1>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #1e1e1e', marginBottom: '20px' }}>
        {['Standings', 'Matches', 'Teams'].map(t => (
          <button key={t} onClick={() => setTab(t)} style={{ padding: '10px 20px', background: 'none', border: 'none', color: tab === t ? gold : '#555', fontSize: '13px', fontWeight: tab === t ? '700' : '400', cursor: 'pointer', borderBottom: tab === t ? `2px solid ${gold}` : '2px solid transparent' }}>
            {t}
          </button>
        ))}
      </div>

      {/* STANDINGS */}
      {tab === 'Standings' && (
        <div style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #1e1e1e' }}>
                {['#', 'Team', 'MP', 'W', 'L', 'DW', 'DL', 'PTS'].map(h => (
                  <th key={h} style={{ padding: '12px 16px', color: gold, fontSize: '10px', letterSpacing: '2px', textAlign: h === 'Team' ? 'left' : 'center', fontWeight: '700' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {standings.map((s, i) => (
                <tr key={s.id} style={{ borderBottom: '1px solid #1a1a1a' }}>
                  <td style={{ padding: '12px 16px', color: i < 2 ? gold : '#555', fontWeight: '700', textAlign: 'center' }}>{i + 1}</td>
                  <td style={{ padding: '12px 16px', color: '#fff', fontWeight: '600' }}>{getTeamName(s.team_id)}</td>
                  <td style={{ padding: '12px 16px', color: '#888', textAlign: 'center' }}>{s.matches_played}</td>
                  <td style={{ padding: '12px 16px', color: '#4caf50', textAlign: 'center' }}>{s.wins}</td>
                  <td style={{ padding: '12px 16px', color: '#ff5252', textAlign: 'center' }}>{s.losses}</td>
                  <td style={{ padding: '12px 16px', color: '#888', textAlign: 'center' }}>{s.disciplines_won}</td>
                  <td style={{ padding: '12px 16px', color: '#888', textAlign: 'center' }}>{s.disciplines_lost}</td>
                  <td style={{ padding: '12px 16px', color: gold, fontWeight: '900', fontSize: '16px', textAlign: 'center' }}>{s.points}</td>
                </tr>
              ))}
              {standings.length === 0 && <tr><td colSpan="8" style={{ padding: '24px', textAlign: 'center', color: '#444' }}>No standings yet</td></tr>}
            </tbody>
          </table>
        </div>
      )}

      {/* MATCHES */}
      {tab === 'Matches' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
            <button onClick={() => setShowMatchForm(!showMatchForm)} style={{ padding: '8px 16px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
              + NEW MATCH
            </button>
          </div>
          {showMatchForm && (
            <div style={{ background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '20px', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '6px' }}>HOME TEAM</label>
                  <select value={matchForm.home_team_id} onChange={e => setMatchForm({...matchForm, home_team_id: e.target.value})}
                    style={{ width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none' }}>
                    <option value="">Select...</option>
                    {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '6px' }}>AWAY TEAM</label>
                  <select value={matchForm.away_team_id} onChange={e => setMatchForm({...matchForm, away_team_id: e.target.value})}
                    style={{ width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none' }}>
                    <option value="">Select...</option>
                    {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '6px' }}>DATE</label>
                  <input type="date" value={matchForm.match_date} onChange={e => setMatchForm({...matchForm, match_date: e.target.value})}
                    style={{ width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }} />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '6px' }}>ROUND</label>
                  <input type="number" value={matchForm.round_number} onChange={e => setMatchForm({...matchForm, round_number: e.target.value})}
                    style={{ width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none', boxSizing: 'border-box' }} />
                </div>
                <div>
                  <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '6px' }}>JUDGE 1 (Home)</label>
                  <select value={matchForm.judge_id} onChange={e => setMatchForm({...matchForm, judge_id: e.target.value})}
                    style={{ width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none' }}>
                    <option value="">No judge</option>
                    {judges.map(j => <option key={j.id} value={j.id}>{j.first_name} {j.last_name}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '6px' }}>JUDGE 2 (Away)</label>
                  <select value={matchForm.judge2_id} onChange={e => setMatchForm({...matchForm, judge2_id: e.target.value})}
                    style={{ width: '100%', padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none' }}>
                    <option value="">No judge</option>
                    {judges.map(j => <option key={j.id} value={j.id}>{j.first_name} {j.last_name}</option>)}
                  </select>
                </div>
              </div>
              <div style={{ marginTop: '16px', borderTop: '1px solid #2a2a2a', paddingTop: '16px' }}>
                <label style={{ display: 'block', color: '#888', fontSize: '10px', marginBottom: '10px' }}>
                  SELECT 5 DISCIPLINES ({selectedDisciplines.length}/5)
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '14px' }}>
                  {STANDARD_DISCIPLINES.map(d => {
                    const checked = selectedDisciplines.some(s => s.name === d.name);
                    return (
                      <div key={d.name} onClick={() => {
                        if (checked) {
                          setSelectedDisciplines(selectedDisciplines.filter(s => s.name !== d.name));
                        } else if (selectedDisciplines.length < 5) {
                          setSelectedDisciplines([...selectedDisciplines, d]);
                        }
                      }} style={{
                        padding: '8px 12px', borderRadius: '3px', cursor: 'pointer',
                        border: `1px solid ${checked ? gold : '#2a2a2a'}`,
                        background: checked ? 'rgba(201,168,76,0.1)' : '#0a0a0a',
                        color: checked ? gold : '#666',
                        fontSize: '12px', fontWeight: checked ? '700' : '400',
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                      }}>
                        <span>{d.name}</span>
                        <span style={{ fontSize: '10px', color: '#444' }}>{d.unit}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
              <button onClick={createMatch} style={{ padding: '10px 24px', background: selectedDisciplines.length === 5 ? gold : '#333', color: selectedDisciplines.length === 5 ? '#000' : '#666', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: selectedDisciplines.length === 5 ? 'pointer' : 'not-allowed' }}>
                CREATE MATCH →
              </button>
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {matches.map(m => (
              <div key={m.id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '16px 20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
                    <div style={{ color: '#fff', fontWeight: '700', fontSize: '14px', flex: 1, textAlign: 'right' }}>{getTeamName(m.home_team_id)}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {m.status === 'completed' ? (
                        <div style={{ background: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: '4px', padding: '6px 16px', color: gold, fontWeight: '900', fontSize: '18px' }}>
                          {m.home_score} : {m.away_score}
                        </div>
                      ) : (
                        <div style={{ color: '#444', fontSize: '12px', letterSpacing: '2px' }}>vs</div>
                      )}
                    </div>
                    <div style={{ color: '#fff', fontWeight: '700', fontSize: '14px', flex: 1 }}>{getTeamName(m.away_team_id)}</div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginLeft: '16px' }}>
                    <div style={{ color: '#444', fontSize: '11px' }}>R{m.round_number}</div>
                    <button onClick={() => { setEditResult(m.id); setResultForm({ home_score: m.home_score || 0, away_score: m.away_score || 0 }); }}
                      style={{ padding: '4px 10px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '10px', fontWeight: '700', cursor: 'pointer' }}>
                      RESULT
                    </button>
                    <button onClick={() => navigate(`/asl/matches/${m.id}`)}
                      style={{ padding: '4px 10px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '10px', fontWeight: '700', cursor: 'pointer' }}>
                      PROTOCOL
                    </button>
                    <button onClick={() => deleteMatch(m.id)}
                      style={{ padding: '4px 10px', background: 'transparent', border: '1px solid #ff5252', color: '#ff5252', borderRadius: '3px', fontSize: '10px', fontWeight: '700', cursor: 'pointer' }}>
                      ✕
                    </button>
                  </div>
                </div>
                {editResult === m.id && (
                  <div style={{ marginTop: '12px', display: 'flex', gap: '12px', alignItems: 'center', borderTop: '1px solid #1e1e1e', paddingTop: '12px' }}>
                    <input type="number" min="0" max="5" value={resultForm.home_score} onChange={e => setResultForm({...resultForm, home_score: parseInt(e.target.value)})}
                      style={{ width: '60px', padding: '8px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '16px', textAlign: 'center', outline: 'none' }} />
                    <span style={{ color: '#555' }}>:</span>
                    <input type="number" min="0" max="5" value={resultForm.away_score} onChange={e => setResultForm({...resultForm, away_score: parseInt(e.target.value)})}
                      style={{ width: '60px', padding: '8px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '16px', textAlign: 'center', outline: 'none' }} />
                    <button onClick={saveResult} style={{ padding: '8px 16px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>SAVE</button>
                    <button onClick={() => setEditResult(null)} style={{ padding: '8px 12px', background: 'transparent', border: '1px solid #333', color: '#666', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>✕</button>
                  </div>
                )}
              </div>
            ))}
            {matches.length === 0 && <p style={{ color: '#444', fontSize: '13px' }}>No matches yet.</p>}
          </div>
        </div>
      )}

      {/* TEAMS */}
      {tab === 'Teams' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
            <button onClick={() => setShowAddTeam(!showAddTeam)} style={{ padding: '8px 16px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
              + ADD TEAM
            </button>
          </div>
          {showAddTeam && (
            <div style={{ background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '16px', marginBottom: '16px', display: 'flex', gap: '12px' }}>
              <select value={selectedTeamId} onChange={e => setSelectedTeamId(e.target.value)}
                style={{ flex: 1, padding: '10px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none' }}>
                <option value="">Select team...</option>
                {allTeams.filter(t => !teams.find(dt => dt.id === t.id)).map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
              <button onClick={addTeam} style={{ padding: '10px 20px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>ADD</button>
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {teams.map(t => (
              <div key={t.id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '14px 20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                {t.logo_url ? <img src={`https://ranking.worldstrongman.org${t.logo_url}`} style={{ width: '40px', height: '40px', objectFit: 'contain', borderRadius: '3px' }} />
                  : <div style={{ width: '40px', height: '40px', background: '#1a1a1a', borderRadius: '3px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>👥</div>}
                <div style={{ color: '#fff', fontWeight: '600', fontSize: '14px' }}>{t.name}</div>
                <div style={{ color: '#555', fontSize: '12px' }}>{t.country}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
}
