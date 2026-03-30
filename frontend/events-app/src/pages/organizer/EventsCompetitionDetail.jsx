import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const teal = '#005B5C';
const sand = '#E8D5B5';
const API = 'https://api.events.worldstrongman.org';

const inp = { width: '100%', padding: '10px 14px', border: '1px solid #e8e0d0', borderRadius: '8px', fontSize: '14px', outline: 'none', boxSizing: 'border-box', background: '#fafafa' };
const lbl = { display: 'block', fontSize: '11px', fontWeight: '600', color: '#555', marginBottom: '5px', letterSpacing: '0.5px' };
const btn = { padding: '10px 20px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: '700', cursor: 'pointer' };
const btnOutline = { padding: '10px 20px', background: '#fff', color: teal, border: `1px solid ${teal}`, borderRadius: '8px', fontSize: '13px', fontWeight: '700', cursor: 'pointer' };

const TABS = ['Divisions', 'Athletes', 'Disciplines', 'Judges'];
const GENDERS = ['male', 'female', 'mixed'];
const AGE_GROUPS = ['open', 'junior', 'master', 'master50', 'youth'];
const FORMATS = ['individual', 'relay', 'team'];
const SPORTS = ['strongman', 'strict_curl', 'stick_pulling', 'powerlifting'];

const STRONGMAN_DISCIPLINES = [
  'Log Lift', 'Axle Press', 'Deadlift', 'Car Deadlift', 'Farmers Walk',
  'Atlas Stones', 'Yoke Walk', 'Sandbag Run', 'Tire Flip', 'Keg Toss',
  'Shield Carry', 'Loading Race', 'Medley', 'Custom'
];

export default function EventsCompetitionDetail() {
  const { competitionId } = useParams();
  const navigate = useNavigate();
  const [competition, setCompetition] = useState(null);
  const [tab, setTab] = useState('Divisions');
  const [divisions, setDivisions] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [selectedDivision, setSelectedDivision] = useState(null);
  const [showDivForm, setShowDivForm] = useState(false);
  const [divForm, setDivForm] = useState({ name: '', gender: 'male', weight_min: '', weight_max: '', age_group: 'open', format: 'individual', team_size: '', sport_type: 'strongman' });
  const [disciplines, setDisciplines] = useState([]);
  const [showDiscForm, setShowDiscForm] = useState(false);
  const [discForm, setDiscForm] = useState({ discipline_name: '', discipline_mode: 'max_weight', order_no: 1, notes: '' });
  const [judgeEmail, setJudgeEmail] = useState('');
  const [judgeName, setJudgeName] = useState('');
  const [judgeInvites, setJudgeInvites] = useState([]);
  const [inviting, setInviting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(null);

  useEffect(() => {
    axios.get(`${API}/competitions/${competitionId}`).then(r => setCompetition(r.data)).catch(() => {});
    axios.get(`${API}/divisions/${competitionId}`).then(r => setDivisions(r.data)).catch(() => {});
    axios.get(`${API}/participants/competition/${competitionId}`).then(r => setParticipants(r.data)).catch(() => {});
    axios.get(`${API}/judges/invites/${competitionId}`, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }).then(r => setJudgeInvites(r.data)).catch(() => {});
  }, [competitionId]);

  const loadDisciplines = (divId) => {
    axios.get(`${API}/divisions/${divId}/disciplines`).then(r => setDisciplines(r.data)).catch(() => {});
  };

  const selectDivision = (div) => {
    setSelectedDivision(div);
    loadDisciplines(div.id);
  };

  const createDivision = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/divisions/`, { ...divForm, competition_id: competitionId,
        weight_min: divForm.weight_min ? parseFloat(divForm.weight_min) : null,
        weight_max: divForm.weight_max ? parseFloat(divForm.weight_max) : null,
        team_size: divForm.team_size ? parseInt(divForm.team_size) : null,
      }, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });
      const r = await axios.get(`${API}/divisions/${competitionId}`);
      setDivisions(r.data);
      setShowDivForm(false);
      setDivForm({ name: '', gender: 'male', weight_min: '', weight_max: '', age_group: 'open', format: 'individual', team_size: '', sport_type: 'strongman' });
    } catch(e) { alert('Error creating division'); }
    setSaving(false);
  };

  const createDiscipline = async () => {
    if (!selectedDivision) return;
    setSaving(true);
    try {
      await axios.post(`${API}/divisions/${selectedDivision.id}/disciplines`,
        { ...discForm, order_no: parseInt(discForm.order_no) || 1 },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      loadDisciplines(selectedDivision.id);
      setShowDiscForm(false);
      setDiscForm({ discipline_name: '', discipline_mode: 'max_weight', order_no: disciplines.length + 2, notes: '' });
    } catch(e) { alert('Error creating discipline'); }
    setSaving(false);
  };

  const inviteJudge = async () => {
    if (!judgeEmail) return;
    setInviting(true);
    try {
      await axios.post(`${API}/judges/invite`,
        { competition_id: competitionId, email: judgeEmail, name: judgeName },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      const r = await axios.get(`${API}/judges/invites/${competitionId}`, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });
      setJudgeInvites(r.data);
      setJudgeEmail(''); setJudgeName('');
    } catch(e) { alert('Error sending invite'); }
    setInviting(false);
  };

  const copyLink = (url, id) => {
    navigator.clipboard.writeText(url);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  if (!competition) return <div style={{ minHeight: '100vh', background: '#f7f4ef', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>Loading...</div>;

  return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef' }}>
      {/* Header */}
      <div style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '16px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '36px', height: '36px', background: teal, borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', fontWeight: '800', color: sand, cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>W</div>
          <div>
            <div style={{ fontSize: '11px', color: '#888', cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>← Dashboard</div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#1a1a1a' }}>{competition.name}</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '11px', fontWeight: '700', padding: '3px 10px', borderRadius: '4px', background: competition.status === 'PUBLISHED' ? '#e8f5e9' : '#fff3e0', color: competition.status === 'PUBLISHED' ? '#2e7d32' : '#e07b00' }}>{competition.status}</span>
          <button onClick={() => { const url = `${window.location.origin}/tournament/${competitionId}/register`; copyLink(url, 'reg'); }} style={{ ...btnOutline, fontSize: '12px', padding: '7px 14px' }}>
            {copied === 'reg' ? '✅ Copied!' : '🔗 Registration link'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '0 24px', display: 'flex', gap: '0' }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: '14px 20px', border: 'none', borderBottom: tab === t ? `2px solid ${teal}` : '2px solid transparent', background: 'none', fontSize: '13px', fontWeight: tab === t ? '700' : '500', color: tab === t ? teal : '#888', cursor: 'pointer' }}>
            {t} {t === 'Athletes' && participants.length > 0 ? `(${participants.length})` : ''}
            {t === 'Divisions' && divisions.length > 0 ? `(${divisions.length})` : ''}
          </button>
        ))}
      </div>

      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 24px' }}>

        {/* DIVISIONS TAB */}
        {tab === 'Divisions' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#1a1a1a', margin: 0 }}>Divisions</h2>
              <button onClick={() => setShowDivForm(!showDivForm)} style={btn}>+ Add Division</button>
            </div>

            {showDivForm && (
              <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '15px', fontWeight: '700', margin: '0 0 20px' }}>New Division</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ gridColumn: '1/-1' }}>
                    <label style={lbl}>DIVISION NAME *</label>
                    <input value={divForm.name} onChange={e => setDivForm({...divForm, name: e.target.value})} placeholder="e.g. Men Open U110 kg" style={inp} />
                  </div>
                  <div>
                    <label style={lbl}>SPORT</label>
                    <select value={divForm.sport_type} onChange={e => setDivForm({...divForm, sport_type: e.target.value})} style={inp}>
                      {SPORTS.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                    </select>
                  </div>
                  <div>
                    <label style={lbl}>GENDER</label>
                    <select value={divForm.gender} onChange={e => setDivForm({...divForm, gender: e.target.value})} style={inp}>
                      {GENDERS.map(g => <option key={g} value={g}>{g}</option>)}
                    </select>
                  </div>
                  <div>
                    <label style={lbl}>WEIGHT MIN (kg)</label>
                    <input type="number" value={divForm.weight_min} onChange={e => setDivForm({...divForm, weight_min: e.target.value})} placeholder="e.g. 80" style={inp} />
                  </div>
                  <div>
                    <label style={lbl}>WEIGHT MAX (kg)</label>
                    <input type="number" value={divForm.weight_max} onChange={e => setDivForm({...divForm, weight_max: e.target.value})} placeholder="e.g. 110" style={inp} />
                  </div>
                  <div>
                    <label style={lbl}>AGE GROUP</label>
                    <select value={divForm.age_group} onChange={e => setDivForm({...divForm, age_group: e.target.value})} style={inp}>
                      {AGE_GROUPS.map(a => <option key={a} value={a}>{a}</option>)}
                    </select>
                  </div>
                  <div>
                    <label style={lbl}>FORMAT</label>
                    <select value={divForm.format} onChange={e => setDivForm({...divForm, format: e.target.value})} style={inp}>
                      {FORMATS.map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                  </div>
                  {divForm.format === 'team' && (
                    <div>
                      <label style={lbl}>TEAM SIZE</label>
                      <input type="number" value={divForm.team_size} onChange={e => setDivForm({...divForm, team_size: e.target.value})} placeholder="e.g. 3" style={inp} />
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
                  <button onClick={createDivision} disabled={saving} style={btn}>{saving ? 'Saving...' : 'Create Division'}</button>
                  <button onClick={() => setShowDivForm(false)} style={btnOutline}>Cancel</button>
                </div>
              </div>
            )}

            {divisions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '60px 20px', color: '#aaa', background: '#fff', borderRadius: '12px', border: '1px solid #e8e0d0' }}>
                <div style={{ fontSize: '40px', marginBottom: '12px' }}>📋</div>
                <p>No divisions yet. Add your first division.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {divisions.map(d => (
                  <div key={d.id} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '10px', padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '700', fontSize: '15px', color: '#1a1a1a' }}>{d.name}</div>
                      <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                        {d.gender} · {d.age_group} · {d.format}
                        {d.weight_min && d.weight_max ? ` · ${d.weight_min}–${d.weight_max} kg` : ''}
                        {` · ${d.sport_type}`}
                      </div>
                    </div>
                    <div style={{ fontSize: '12px', color: '#aaa' }}>
                      {participants.filter(p => p.events_division_id === d.id).length} athletes
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ATHLETES TAB */}
        {tab === 'Athletes' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#1a1a1a', margin: 0 }}>Athletes ({participants.length})</h2>
              <button onClick={() => { const url = `${window.location.origin}/tournament/${competitionId}/register`; copyLink(url, 'reg2'); }} style={btnOutline}>
                {copied === 'reg2' ? '✅ Copied!' : '🔗 Copy registration link'}
              </button>
            </div>
            {participants.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '60px 20px', color: '#aaa', background: '#fff', borderRadius: '12px', border: '1px solid #e8e0d0' }}>
                <div style={{ fontSize: '40px', marginBottom: '12px' }}>👥</div>
                <p>No athletes registered yet.</p>
                <p style={{ fontSize: '12px' }}>Share the registration link to invite athletes.</p>
              </div>
            ) : (
              <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #e8e0d0', background: '#fafafa' }}>
                      {['#', 'Name', 'Country', 'Weight', 'Division', 'Status'].map(h => (
                        <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '700', color: '#888', letterSpacing: '0.5px' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {participants.map((p, i) => (
                      <tr key={p.id} style={{ borderBottom: '1px solid #f0ebe3' }}>
                        <td style={{ padding: '12px 16px', fontSize: '13px', color: '#888' }}>{p.bib_no || i + 1}</td>
                        <td style={{ padding: '12px 16px', fontSize: '14px', fontWeight: '600', color: '#1a1a1a' }}>{p.first_name} {p.last_name}</td>
                        <td style={{ padding: '12px 16px', fontSize: '13px', color: '#666' }}>{p.country || '—'}</td>
                        <td style={{ padding: '12px 16px', fontSize: '13px', color: '#666' }}>{p.bodyweight_kg ? `${p.bodyweight_kg} kg` : '—'}</td>
                        <td style={{ padding: '12px 16px', fontSize: '13px', color: '#666' }}>{p.division_name || '—'}</td>
                        <td style={{ padding: '12px 16px' }}>
                          <span style={{ fontSize: '11px', fontWeight: '700', padding: '2px 8px', borderRadius: '4px', background: p.status === 'confirmed' ? '#e8f5e9' : '#fff3e0', color: p.status === 'confirmed' ? '#2e7d32' : '#e07b00' }}>{p.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* DISCIPLINES TAB */}
        {tab === 'Disciplines' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#1a1a1a', margin: 0 }}>Disciplines</h2>
            </div>

            {divisions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '60px 20px', color: '#aaa', background: '#fff', borderRadius: '12px', border: '1px solid #e8e0d0' }}>
                <p>Create divisions first, then add disciplines.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '20px' }}>
                {/* Division selector */}
                <div style={{ width: '220px', flexShrink: 0 }}>
                  <div style={{ fontSize: '11px', fontWeight: '700', color: '#888', marginBottom: '8px', letterSpacing: '0.5px' }}>SELECT DIVISION</div>
                  {divisions.map(d => (
                    <div key={d.id} onClick={() => selectDivision(d)}
                      style={{ padding: '10px 14px', borderRadius: '8px', marginBottom: '6px', cursor: 'pointer', background: selectedDivision?.id === d.id ? teal : '#fff', color: selectedDivision?.id === d.id ? '#fff' : '#1a1a1a', border: `1px solid ${selectedDivision?.id === d.id ? teal : '#e8e0d0'}`, fontSize: '13px', fontWeight: '600' }}>
                      {d.name}
                    </div>
                  ))}
                </div>

                {/* Disciplines list */}
                <div style={{ flex: 1 }}>
                  {!selectedDivision ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: '#aaa', background: '#fff', borderRadius: '12px', border: '1px solid #e8e0d0' }}>
                      Select a division to manage disciplines
                    </div>
                  ) : (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <div style={{ fontSize: '14px', fontWeight: '700', color: '#1a1a1a' }}>{selectedDivision.name}</div>
                        <button onClick={() => setShowDiscForm(!showDiscForm)} style={btn}>+ Add Discipline</button>
                      </div>

                      {showDiscForm && (
                        <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '10px', padding: '20px', marginBottom: '16px' }}>
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                            <div style={{ gridColumn: '1/-1' }}>
                              <label style={lbl}>DISCIPLINE *</label>
                              <select value={discForm.discipline_name} onChange={e => setDiscForm({...discForm, discipline_name: e.target.value})} style={inp}>
                                <option value="">Select discipline</option>
                                {STRONGMAN_DISCIPLINES.map(d => <option key={d} value={d}>{d}</option>)}
                              </select>
                              {discForm.discipline_name === 'Custom' && (
                                <input style={{...inp, marginTop: '8px'}} placeholder="Custom discipline name" onChange={e => setDiscForm({...discForm, discipline_name: e.target.value})} />
                              )}
                            </div>
                            <div>
                              <label style={lbl}>SCORING MODE</label>
                              <select value={discForm.discipline_mode} onChange={e => setDiscForm({...discForm, discipline_mode: e.target.value})} style={inp}>
                                <option value="max_weight">Max Weight</option>
                                <option value="max_reps">Max Reps</option>
                                <option value="time">Time (fastest)</option>
                                <option value="distance">Distance</option>
                                <option value="points">Points</option>
                              </select>
                            </div>
                            <div>
                              <label style={lbl}>ORDER #</label>
                              <input type="number" value={discForm.order_no} onChange={e => setDiscForm({...discForm, order_no: e.target.value})} style={inp} />
                            </div>
                            <div style={{ gridColumn: '1/-1' }}>
                              <label style={lbl}>NOTES</label>
                              <input value={discForm.notes} onChange={e => setDiscForm({...discForm, notes: e.target.value})} placeholder="e.g. 180kg implement, 60 sec time cap" style={inp} />
                            </div>
                          </div>
                          <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                            <button onClick={createDiscipline} disabled={saving} style={btn}>{saving ? 'Saving...' : 'Add'}</button>
                            <button onClick={() => setShowDiscForm(false)} style={btnOutline}>Cancel</button>
                          </div>
                        </div>
                      )}

                      {disciplines.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '40px', color: '#aaa', background: '#fff', borderRadius: '12px', border: '1px solid #e8e0d0' }}>
                          No disciplines yet
                        </div>
                      ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          {disciplines.map((d, i) => (
                            <div key={d.id} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '8px', padding: '14px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                                <span style={{ width: '24px', height: '24px', background: teal, color: '#fff', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: '800', flexShrink: 0 }}>{i + 1}</span>
                                <div>
                                  <div style={{ fontWeight: '700', fontSize: '14px', color: '#1a1a1a' }}>{d.discipline_name}</div>
                                  {d.notes && <div style={{ fontSize: '12px', color: '#888', marginTop: '2px' }}>{d.notes}</div>}
                                </div>
                              </div>
                              <span style={{ fontSize: '11px', fontWeight: '600', color: teal, background: '#e8f4f4', padding: '3px 10px', borderRadius: '4px' }}>{d.discipline_mode?.replace('_', ' ')}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* JUDGES TAB */}
        {tab === 'Judges' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '800', color: '#1a1a1a', margin: 0 }}>Judges</h2>
            </div>

            <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '700', margin: '0 0 16px' }}>Invite Judge by Email</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
                <div>
                  <label style={lbl}>EMAIL *</label>
                  <input type="email" value={judgeEmail} onChange={e => setJudgeEmail(e.target.value)} placeholder="judge@example.com" style={inp} />
                </div>
                <div>
                  <label style={lbl}>NAME</label>
                  <input value={judgeName} onChange={e => setJudgeName(e.target.value)} placeholder="Judge name" style={inp} />
                </div>
              </div>
              <button onClick={inviteJudge} disabled={inviting || !judgeEmail} style={{ ...btn, opacity: inviting || !judgeEmail ? 0.6 : 1 }}>
                {inviting ? 'Sending...' : 'Send Invite →'}
              </button>
            </div>

            {judgeInvites.length > 0 && (
              <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', overflow: 'hidden' }}>
                <div style={{ padding: '16px 20px', borderBottom: '1px solid #e8e0d0', fontSize: '13px', fontWeight: '700', color: '#1a1a1a' }}>Sent Invites</div>
                {judgeInvites.map(inv => (
                  <div key={inv.id} style={{ padding: '14px 20px', borderBottom: '1px solid #f0ebe3', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '14px' }}>{inv.name || inv.email}</div>
                      <div style={{ fontSize: '12px', color: '#888' }}>{inv.email}</div>
                    </div>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                      <span style={{ fontSize: '11px', fontWeight: '700', padding: '2px 8px', borderRadius: '4px', background: inv.status === 'used' ? '#e8f5e9' : '#fff3e0', color: inv.status === 'used' ? '#2e7d32' : '#e07b00' }}>{inv.status}</span>
                      {inv.status === 'pending' && (
                        <button onClick={() => copyLink(`https://events.worldstrongman.org/judge/${inv.token}`, inv.id)} style={{ ...btnOutline, fontSize: '11px', padding: '5px 10px' }}>
                          {copied === inv.id ? '✅' : '🔗 Copy link'}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
