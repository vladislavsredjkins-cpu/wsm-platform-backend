import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import DisciplinesTab from '../../components/DisciplinesTab';
import api from '../../api';

const gold = '#c9a84c';
const labelStyle = { display: 'block', color: '#888', fontSize: '11px', fontWeight: '600', letterSpacing: '1px', marginBottom: '6px' };
const inputStyle = { width: '100%', padding: '11px 14px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '14px', outline: 'none', boxSizing: 'border-box' };

const TABS = ['Divisions', 'Athletes', 'Disciplines'];

const COUNTRIES = [
  'LAT','LTU','EST','RUS','UKR','BLR','POL','GER','FRA','GBR','ESP','ITA',
  'USA','CAN','AUS','NZL','UAE','KAZ','UZB','TUR','FIN','SWE','NOR','DEN',
  'CZE','SVK','HUN','ROU','BUL','SRB','HRV','SVN','GEO','ARM','AZE','ISR',
];

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

  // Athletes tab
  const [selectedDivision, setSelectedDivision] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showNewAthlete, setShowNewAthlete] = useState(false);
  const [newAthlete, setNewAthlete] = useState({ first_name: '', last_name: '', country: '', gender: 'MEN', date_of_birth: '', email: '' });
  const [registerForm, setRegisterForm] = useState({ bib_no: '', bodyweight_kg: '' });
  const [selectedAthlete, setSelectedAthlete] = useState(null);
  const [savingAthlete, setSavingAthlete] = useState(false);

  const loadDivisions = useCallback(() => {
    return api.get(`/divisions/competition/${competitionId}`).then(r => setDivisions(r.data));
  }, [competitionId]);

  useEffect(() => {
    Promise.all([
      api.get(`/competitions/${competitionId}`),
      loadDivisions(),
    ]).then(([compRes]) => {
      setCompetition(compRes.data);
    }).finally(() => setLoading(false));
  }, [competitionId]);

  const loadParticipants = async (divisionId) => {
    const res = await api.get(`/athletes/division/${divisionId}`);
    setParticipants(res.data);
  };

  const selectDivision = (div) => {
    setSelectedDivision(div);
    loadParticipants(div.id);
    setSearchQuery('');
    setSearchResults([]);
    setSelectedAthlete(null);
    setShowNewAthlete(false);
  };

  const handleSearch = async (q) => {
    setSearchQuery(q);
    if (q.length < 2) { setSearchResults([]); return; }
    const res = await api.get(`/athletes/search?q=${q}`);
    setSearchResults(res.data);
  };

  const handleRegister = async () => {
    if (!selectedAthlete || !selectedDivision) return;
    setSavingAthlete(true);
    try {
      await api.post('/athletes/register', {
        athlete_id: selectedAthlete.id,
        competition_division_id: selectedDivision.id,
        bib_no: registerForm.bib_no ? parseInt(registerForm.bib_no) : null,
        bodyweight_kg: registerForm.bodyweight_kg ? parseFloat(registerForm.bodyweight_kg) : null,
      });
      await loadParticipants(selectedDivision.id);
      setSelectedAthlete(null);
      setSearchQuery('');
      setSearchResults([]);
      setRegisterForm({ bib_no: '', bodyweight_kg: '' });
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to register');
    } finally {
      setSavingAthlete(false);
    }
  };

  const handleCreateAndRegister = async () => {
    if (!newAthlete.first_name || !newAthlete.last_name) return alert('Name required');
    setSavingAthlete(true);
    try {
      const res = await api.post('/athletes/', {
        first_name: newAthlete.first_name,
        last_name: newAthlete.last_name,
        country: newAthlete.country || null,
        gender: newAthlete.gender || null,
        date_of_birth: newAthlete.date_of_birth || null,
        email: newAthlete.email || null,
      });
      await api.post('/athletes/register', {
        athlete_id: res.data.id,
        competition_division_id: selectedDivision.id,
        bib_no: registerForm.bib_no ? parseInt(registerForm.bib_no) : null,
        bodyweight_kg: registerForm.bodyweight_kg ? parseFloat(registerForm.bodyweight_kg) : null,
      });
      await loadParticipants(selectedDivision.id);
      setShowNewAthlete(false);
      setNewAthlete({ first_name: '', last_name: '', country: '', gender: 'MEN', date_of_birth: '', email: '' });
      setRegisterForm({ bib_no: '', bodyweight_kg: '' });
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to create athlete');
    } finally {
      setSavingAthlete(false);
    }
  };

  const removeParticipant = async (participantId) => {
    if (!confirm('Remove athlete from this division?')) return;
    await api.delete(`/athletes/participants/${participantId}`);
    await loadParticipants(selectedDivision.id);
  };

  const createDivision = async () => {
    if (!divForm.division_key) return alert('Division key required');
    setSavingDiv(true);
    try {
      const res = await api.post('/divisions/', {
        competition_id: competitionId,
        division_key: divForm.division_key,
        format: divForm.format,
      });
      await loadDivisions();
      setShowDivForm(false);
      setDivForm({ division_key: '', format: 'CLASSIC' });
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to create division');
    } finally {
      setSavingDiv(false);
    }
  };

  if (loading) return <Layout><p style={{ color: '#555' }}>Loading...</p></Layout>;
  if (!competition) return <Layout><p style={{ color: '#555' }}>Not found</p></Layout>;

  return (
    <Layout>
      {/* Breadcrumb */}
      <div style={{ marginBottom: '20px', fontSize: '13px', color: '#555', display: 'flex', gap: '8px' }}>
        <button onClick={() => navigate('/organizer/competitions')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>Competitions</button>
        <span>›</span>
        <span style={{ color: '#888' }}>{competition.name}</span>
      </div>

      {/* Header */}
      <div style={{ marginBottom: '28px', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ color: '#fff', fontSize: '24px', fontWeight: '700', margin: '0 0 6px' }}>{competition.name}</h1>
          <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>
            {competition.date_start || 'No date'}{competition.city ? ` · ${competition.city}` : ''}{competition.country ? ` · ${competition.country}` : ''}
          </p>
        </div>
        <div style={{ background: 'rgba(201,168,76,0.1)', color: gold, fontSize: '13px', fontWeight: '700', padding: '8px 16px', borderRadius: '3px', border: `1px solid rgba(201,168,76,0.3)` }}>
          Q {competition.coefficient_q}
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '24px', borderBottom: '1px solid #1e1e1e' }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            background: 'none', border: 'none', color: tab === t ? gold : '#555',
            padding: '10px 20px', cursor: 'pointer', fontSize: '13px', fontWeight: tab === t ? '700' : '400',
            borderBottom: tab === t ? `2px solid ${gold}` : '2px solid transparent', marginBottom: '-1px',
          }}>{t}</button>
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
                  <label style={labelStyle}>Division</label>
                  <select style={inputStyle} value={divForm.division_key} onChange={e => setDivForm(f => ({ ...f, division_key: e.target.value }))}>
                    <option value="">Select division</option>
                    <optgroup label="— Men —">
                      <option value="MEN_YOUTH_16">Men Youth U16</option>
                      <option value="MEN_YOUTH_18">Men Youth U18</option>
                      <option value="MEN_JUNIOR">Men Junior U23</option>
                      <option value="MEN_SENIOR">Men Senior (Open)</option>
                      <option value="MEN_MASTERS_40">Men Masters 40+</option>
                      <option value="MEN_MASTERS_50">Men Masters 50+</option>
                    </optgroup>
                    <optgroup label="— Women —">
                      <option value="WOMEN_YOUTH_16">Women Youth U16</option>
                      <option value="WOMEN_YOUTH_18">Women Youth U18</option>
                      <option value="WOMEN_JUNIOR">Women Junior U23</option>
                      <option value="WOMEN_SENIOR">Women Senior (Open)</option>
                      <option value="WOMEN_MASTERS_40">Women Masters 40+</option>
                      <option value="WOMEN_MASTERS_50">Women Masters 50+</option>
                    </optgroup>
                    <optgroup label="— Para —">
                      <option value="PARA_MEN">Para Men</option>
                      <option value="PARA_WOMEN">Para Women</option>
                    </optgroup>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>Format</label>
                  <select style={inputStyle} value={divForm.format} onChange={e => setDivForm(f => ({ ...f, format: e.target.value }))}>
                    <option value="CLASSIC">Classic</option>
                    <option value="RELAY">Relay</option>
                    <option value="TEAM_BATTLE">Team Battle</option>
                    <option value="PARA">Para</option>
                  </select>
                </div>
              </div>
              <button onClick={createDivision} disabled={savingDiv} style={{ marginTop: '16px', padding: '10px 28px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
                {savingDiv ? 'CREATING...' : 'CREATE →'}
              </button>
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {divisions.map(d => (
              <div key={d.id}
                onClick={() => { setTab('Athletes'); selectDivision(d); }}
                style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '18px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
                onMouseEnter={e => e.currentTarget.style.borderColor = gold}
                onMouseLeave={e => e.currentTarget.style.borderColor = '#1e1e1e'}
              >
                <div>
                  <div style={{ color: '#fff', fontWeight: '600', fontSize: '15px', marginBottom: '3px' }}>{d.division_key}</div>
                  <div style={{ color: '#555', fontSize: '12px' }}>{d.format} · {d.status}</div>
                </div>
                <StatusBadge status={d.status} />
              </div>
            ))}
            {divisions.length === 0 && <p style={{ color: '#444' }}>No divisions yet.</p>}
          </div>
        </div>
      )}

      {/* ATHLETES TAB */}
      {tab === 'Athletes' && (
        <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: '24px' }}>
          {/* Division selector */}
          <div>
            <div style={{ color: '#888', fontSize: '11px', fontWeight: '600', letterSpacing: '1px', marginBottom: '12px' }}>DIVISION</div>
            {divisions.map(d => (
              <div key={d.id}
                onClick={() => selectDivision(d)}
                style={{ padding: '10px 14px', borderRadius: '3px', cursor: 'pointer', marginBottom: '4px', background: selectedDivision?.id === d.id ? 'rgba(201,168,76,0.1)' : 'transparent', border: selectedDivision?.id === d.id ? `1px solid rgba(201,168,76,0.3)` : '1px solid transparent', color: selectedDivision?.id === d.id ? gold : '#888', fontSize: '13px', fontWeight: selectedDivision?.id === d.id ? '600' : '400' }}
              >
                {d.division_key}
              </div>
            ))}
            {divisions.length === 0 && <p style={{ color: '#444', fontSize: '13px' }}>No divisions yet.</p>}
          </div>

          {/* Athletes panel */}
          <div>
            {!selectedDivision ? (
              <p style={{ color: '#444' }}>Select a division to manage athletes.</p>
            ) : (
              <>
                <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <h3 style={{ color: '#fff', margin: 0, fontSize: '16px' }}>{selectedDivision.division_key} <span style={{ color: '#555', fontWeight: '400', fontSize: '13px' }}>({participants.length} athletes)</span></h3>
                  <button onClick={() => { setShowNewAthlete(!showNewAthlete); setSelectedAthlete(null); setSearchQuery(''); setSearchResults([]); }} style={{ padding: '7px 16px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
                    {showNewAthlete ? 'CANCEL' : '+ NEW ATHLETE'}
                  </button>
                </div>

                {/* Search existing */}
                {!showNewAthlete && (
                  <div style={{ marginBottom: '20px' }}>
                    <label style={labelStyle}>Search & Register Existing Athlete</label>
                    <input
                      style={inputStyle}
                      placeholder="Type name..."
                      value={searchQuery}
                      onChange={e => handleSearch(e.target.value)}
                    />
                    {searchResults.length > 0 && (
                      <div style={{ background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', marginTop: '4px' }}>
                        {searchResults.map(a => (
                          <div key={a.id}
                            onClick={() => { setSelectedAthlete(a); setSearchQuery(`${a.first_name} ${a.last_name}`); setSearchResults([]); }}
                            style={{ padding: '10px 14px', cursor: 'pointer', borderBottom: '1px solid #1a1a1a', color: selectedAthlete?.id === a.id ? gold : '#fff', fontSize: '14px' }}
                            onMouseEnter={e => e.currentTarget.style.background = '#111'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                          >
                            {a.first_name} {a.last_name} <span style={{ color: '#555', fontSize: '12px' }}>· {a.country || '—'}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {selectedAthlete && (
                      <div style={{ marginTop: '12px', background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '16px' }}>
                        <div style={{ color: gold, fontSize: '13px', fontWeight: '600', marginBottom: '12px' }}>
                          ✓ {selectedAthlete.first_name} {selectedAthlete.last_name} · {selectedAthlete.country || '—'}
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                          <div>
                            <label style={labelStyle}>BIB Number</label>
                            <input style={inputStyle} type="number" placeholder="1" value={registerForm.bib_no} onChange={e => setRegisterForm(f => ({ ...f, bib_no: e.target.value }))} />
                          </div>
                          <div>
                            <label style={labelStyle}>Bodyweight (kg)</label>
                            <input style={inputStyle} type="number" step="0.1" placeholder="95.5" value={registerForm.bodyweight_kg} onChange={e => setRegisterForm(f => ({ ...f, bodyweight_kg: e.target.value }))} />
                          </div>
                        </div>
                        <button onClick={handleRegister} disabled={savingAthlete} style={{ marginTop: '12px', padding: '10px 24px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
                          {savingAthlete ? 'REGISTERING...' : 'REGISTER →'}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* New athlete form */}
                {showNewAthlete && (
                  <div style={{ background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '20px', marginBottom: '20px' }}>
                    <div style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px', marginBottom: '16px' }}>NEW ATHLETE</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                      <div>
                        <label style={labelStyle}>First Name</label>
                        <input style={inputStyle} placeholder="John" value={newAthlete.first_name} onChange={e => setNewAthlete(f => ({ ...f, first_name: e.target.value }))} />
                      </div>
                      <div>
                        <label style={labelStyle}>Last Name</label>
                        <input style={inputStyle} placeholder="Smith" value={newAthlete.last_name} onChange={e => setNewAthlete(f => ({ ...f, last_name: e.target.value }))} />
                      </div>
                      <div>
                        <label style={labelStyle}>Country</label>
                        <select style={inputStyle} value={newAthlete.country} onChange={e => setNewAthlete(f => ({ ...f, country: e.target.value }))}>
                          <option value="">Select country</option>
                          {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </div>
                      <div>
                        <label style={labelStyle}>Gender</label>
                        <select style={inputStyle} value={newAthlete.gender} onChange={e => setNewAthlete(f => ({ ...f, gender: e.target.value }))}>
                          <option value="MEN">Men</option>
                          <option value="WOMEN">Women</option>
                        </select>
                      </div>
                      <div>
                        <label style={labelStyle}>Date of Birth</label>
                        <input style={inputStyle} type="date" value={newAthlete.date_of_birth} onChange={e => setNewAthlete(f => ({ ...f, date_of_birth: e.target.value }))} />
                      </div>
                      <div>
                        <label style={labelStyle}>Email</label>
                        <input style={inputStyle} type="email" placeholder="athlete@email.com" value={newAthlete.email} onChange={e => setNewAthlete(f => ({ ...f, email: e.target.value }))} />
                      </div>
                      <div>
                        <label style={labelStyle}>BIB Number</label>
                        <input style={inputStyle} type="number" placeholder="1" value={registerForm.bib_no} onChange={e => setRegisterForm(f => ({ ...f, bib_no: e.target.value }))} />
                      </div>
                      <div>
                        <label style={labelStyle}>Bodyweight (kg)</label>
                        <input style={inputStyle} type="number" step="0.1" placeholder="95.5" value={registerForm.bodyweight_kg} onChange={e => setRegisterForm(f => ({ ...f, bodyweight_kg: e.target.value }))} />
                      </div>
                    </div>
                    <button onClick={handleCreateAndRegister} disabled={savingAthlete} style={{ marginTop: '16px', padding: '10px 28px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
                      {savingAthlete ? 'SAVING...' : 'CREATE & REGISTER →'}
                    </button>
                  </div>
                )}

                {/* Participants list */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {participants.map(p => (
                    <div key={p.id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                        <div style={{ color: gold, fontSize: '12px', fontWeight: '700', width: '32px' }}>#{p.bib_no || '—'}</div>
                        <div>
                          <div style={{ color: '#fff', fontWeight: '600', fontSize: '14px' }}>{p.first_name} {p.last_name}</div>
                          <div style={{ color: '#555', fontSize: '12px' }}>{p.country || '—'} {p.bodyweight_kg ? `· ${p.bodyweight_kg} kg` : ''}</div>
                        </div>
                      </div>
                      <button onClick={() => removeParticipant(p.id)} style={{ background: 'transparent', border: '1px solid #2a2a2a', color: '#555', padding: '4px 10px', borderRadius: '3px', cursor: 'pointer', fontSize: '11px' }}>
                        Remove
                      </button>
                    </div>
                  ))}
                  {participants.length === 0 && <p style={{ color: '#444' }}>No athletes registered yet.</p>}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* DISCIPLINES TAB */}
      {tab === 'Disciplines' && (
        <DisciplinesTab divisions={divisions} competitionId={competitionId} />
      )}
    </Layout>
  );
}

function StatusBadge({ status }) {
  const colors = {
    OPEN: { bg: 'rgba(76,175,80,0.1)', color: '#4caf50' },
    LOCKED: { bg: 'rgba(255,152,0,0.1)', color: '#ff9800' },
    DRAFT: { bg: 'rgba(100,100,100,0.1)', color: '#888' },
    APPROVED: { bg: 'rgba(33,150,243,0.1)', color: '#2196f3' },
    LIVE: { bg: 'rgba(76,175,80,0.1)', color: '#4caf50' },
  };
  const style = colors[status] || colors.DRAFT;
  return (
    <div style={{ background: style.bg, color: style.color, fontSize: '11px', fontWeight: '700', padding: '3px 10px', borderRadius: '2px' }}>
      {status}
    </div>
  );
}
