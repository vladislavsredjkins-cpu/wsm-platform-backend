import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api';
import Layout from '../../components/Layout';
import DisciplinesTab from '../../components/DisciplinesTab';
import DrawTab from '../../components/DrawTab';
import MCTab from '../../components/MCTab';
import { divisionLabel } from '../../constants/divisions';

const gold = '#c9a84c';
const WEIGHT_OPTIONS = {
  MEN: [['U70','Featherweight (–70kg)'],['U80','Lightweight (–80kg)'],['U95','Middleweight (–95kg)'],['U110','Heavyweight (–110kg)'],['O110','Super Heavyweight (110kg+)']],
  WOMEN: [['U55','Featherweight (–55kg)'],['U65','Lightweight (–65kg)'],['U75','Middleweight (–75kg)'],['U85','Heavyweight (–85kg)'],['O85','Super Heavyweight (85kg+)']],
  PARA_MEN: [['OPEN','Open'],['U80','Up to 80kg'],['O80','Over 80kg']],
  PARA_WOMEN: [['OPEN','Open'],['U80','Up to 80kg'],['O80','Over 80kg']],
};
const inputStyle = { width: '100%', padding: '10px 14px', background: '#0a0a0a', border: '1px solid #2a2a2a', color: '#fff', borderRadius: '3px', fontSize: '13px', outline: 'none' };
const labelStyle = { display: 'block', color: '#555', fontSize: '10px', letterSpacing: '2px', marginBottom: '6px' };
const TABS = ['Divisions', 'Athletes', 'Disciplines', 'Judges', 'Start Order', 'Protocol', 'MC', 'Registrations'];

export default function CompetitionDetail() {
  const { competitionId } = useParams();
  const [competition, setCompetition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('Divisions');
  const [divisions, setDivisions] = useState([]);
  const [showDivForm, setShowDivForm] = useState(false);
  const [divForm, setDivForm] = useState({ division_key: '', format: 'CLASSIC', _gender: '', _age: 'SENIOR', _weight: '' });
  const [selectedDivision, setSelectedDivision] = useState(null);
  const [athletes, setAthletes] = useState([]);
  const [athleteSearch, setAthleteSearch] = useState('');
  const [athleteResults, setAthleteResults] = useState([]);
  const [showNewAthleteForm, setShowNewAthleteForm] = useState(false);
  const [newAthlete, setNewAthlete] = useState({ first_name: '', last_name: '', country: '', email: '' });
  const [bibForm, setBibForm] = useState({});
  const [bwForm, setBwForm] = useState({});
  const [savingAthlete, setSavingAthlete] = useState(false);
  const [judges, setJudges] = useState([]);
  const [judgeSearch, setJudgeSearch] = useState('');
  const [judgeResults, setJudgeResults] = useState([]);
  const [selectedJudge, setSelectedJudge] = useState(null);
  const [judgeRole, setJudgeRole] = useState('Judge');
  const [savingJudge, setSavingJudge] = useState(false);
  const [sponsors, setSponsors] = useState([]);
  const [newSponsor, setNewSponsor] = useState({ name: '', website_url: '', tier: 'FREE' });
  const [bannerUploading, setBannerUploading] = useState(false);
  const [editForm, setEditForm] = useState({ name: '', city: '', country: '', organizer_email: '', date_start: '', date_end: '', entry_fee_enabled: false, entry_fee: '', registration_deadline: '', entry_fee_non_refundable: true });
  const [saving, setSaving] = useState(false);
  const [liveData, setLiveData] = useState(null);
  const [soDiv, setSoDiv] = useState(0);
  const [registrations, setRegistrations] = useState([]);
  const [soDisc, setSoDisc] = useState(0);

  const loadDivisions = useCallback(() => {
    return api.get(`/divisions/competition/${competitionId}`).then(r => setDivisions(r.data));
  }, [competitionId]);

  useEffect(() => {
    Promise.all([
      api.get(`/competitions/${competitionId}`).then(r => {
        setCompetition(r.data);
        setEditForm({ name: r.data.name, city: r.data.city||'', country: r.data.country||'', organizer_email: r.data.organizer_email||'', date_start: r.data.date_start||'', date_end: r.data.date_end||'', entry_fee_enabled: r.data.entry_fee_enabled||false, entry_fee: r.data.entry_fee||'', registration_deadline: r.data.registration_deadline||'', entry_fee_non_refundable: r.data.entry_fee_non_refundable !== false });
      }),
      api.get(`/competitions/${competitionId}/judges`).then(r => setJudges(r.data)),
      api.get(`/competitions/${competitionId}/sponsors`).then(r => setSponsors(r.data)),
      api.get(`/competitions/${competitionId}/live-data`).then(r => setLiveData(r.data)),
      loadDivisions(),
    ]).finally(() => setLoading(false));
  }, [competitionId, loadDivisions]);

  const selectDivision = async (div) => {
    setSelectedDivision(div);
    const res = await api.get(`/athletes/division/${div.id}`);
    setAthletes(res.data);
  };
  const searchAthletes = async (q) => {
    setAthleteSearch(q);
    if (q.length < 2) { setAthleteResults([]); return; }
    const res = await api.get(`/athletes/search?q=${q}`);
    setAthleteResults(res.data);
  };

  const registerAthlete = async (athleteId) => {
    setSavingAthlete(true);
    try {
      await api.post(`/athletes/division/${selectedDivision.id}/register`, {
        athlete_id: athleteId,
        bib_no: parseInt(bibForm[athleteId]) || null,
        bodyweight_kg: parseFloat(bwForm[athleteId]) || null,
      });
      const res = await api.get(`/athletes/division/${selectedDivision.id}`);
      setAthletes(res.data);
      setAthleteSearch(''); setAthleteResults([]);
    } catch(e) { alert(e.response?.data?.detail || 'Error'); }
    finally { setSavingAthlete(false); }
  };

  const createAndRegister = async () => {
    setSavingAthlete(true);
    try {
      const res = await api.post('/athletes/', newAthlete);
      await registerAthlete(res.data.id);
      setNewAthlete({ first_name: '', last_name: '', country: '', email: '' });
      setShowNewAthleteForm(false);
    } catch(e) { alert(e.response?.data?.detail || 'Error'); }
    finally { setSavingAthlete(false); }
  };

  const saveCompetition = async () => {
    // Convert entry_fee to number
    const formToSave = {...editForm, entry_fee: editForm.entry_fee ? parseFloat(editForm.entry_fee) : null};
    setSaving(true);
    try {
      const res = await api.patch(`/competitions/${competitionId}`, formToSave);
      setCompetition(res.data);
    } finally { setSaving(false); }
  };

  const togglePublish = async () => {
    const newStatus = competition.status === 'PUBLISHED' ? 'DRAFT' : 'PUBLISHED';
    const res = await api.patch(`/competitions/${competitionId}`, { status: newStatus });
    setCompetition(res.data);
  };

  const uploadBanner = async (file) => {
    setBannerUploading(true);
    try {
      const fd = new FormData(); fd.append('file', file);
      const res = await api.post(`/competitions/${competitionId}/banner`, fd);
      setCompetition(prev => ({ ...prev, banner_url: res.data.banner_url }));
    } finally { setBannerUploading(false); }
  };

  const addSponsor = async () => {
    if (!newSponsor.name.trim()) return;
    const res = await api.post(`/competitions/${competitionId}/sponsors`, newSponsor);
    setSponsors([...sponsors, res.data]);
    setNewSponsor({ name: '', website_url: '', tier: 'FREE' });
  };

  const deleteSponsor = async (sid) => {
    await api.delete(`/competitions/${competitionId}/sponsors/${sid}`);
    setSponsors(sponsors.filter(s => s.id !== sid));
  };

  const searchJudges = async (q) => {
    setJudgeSearch(q);
    if (q.length < 2) { setJudgeResults([]); return; }
    const res = await api.get(`/judges/search?q=${q}`);
    setJudgeResults(res.data);
  };

  const assignJudge = async () => {
    if (!selectedJudge) return;
    setSavingJudge(true);
    try {
      await api.post(`/competitions/${competitionId}/judges`, { judge_id: selectedJudge.id, role: judgeRole });
      const res = await api.get(`/competitions/${competitionId}/judges`);
      setJudges(res.data);
      setSelectedJudge(null); setJudgeSearch(''); setJudgeResults([]); setJudgeRole('Judge');
    } catch(e) { alert(e.response?.data?.detail || 'Failed to assign judge'); }
    finally { setSavingJudge(false); }
  };

  const removeJudge = async (assignmentId) => {
    if (!confirm('Remove judge from this competition?')) return;
    await api.delete(`/competitions/${competitionId}/judges/${assignmentId}`);
    setJudges(judges.filter(j => j.id !== assignmentId));
  };

  if (loading) return <Layout><p style={{ color: '#555' }}>Loading...</p></Layout>;
  if (!competition) return <Layout><p style={{ color: '#555' }}>Not found</p></Layout>;

  return (
 <Layout> 
  <div style={{ marginBottom: '24px' }}>
        <div style={{ color: '#555', fontSize: '11px', letterSpacing: '2px', marginBottom: '8px' }}>
          <a href="/organizer/competitions" style={{ color: '#555', textDecoration: 'none' }}>Competitions</a> › {competition.name}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1 style={{ color: '#fff', fontSize: '28px', fontWeight: '900', letterSpacing: '3px', margin: 0 }}>{competition.name}</h1>
            <div style={{ color: '#555', fontSize: '12px', letterSpacing: '2px', marginTop: '4px' }}>{competition.date_start} · {competition.city} · {competition.country}</div>
          </div>
  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ padding: '4px 10px', background: '#111', border: '1px solid #333', color: gold, fontSize: '11px', letterSpacing: '2px', borderRadius: '3px' }}>Q {competition.coefficient_q}</span>
            <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/draw`} target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🎲 DRAW</a>
            <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/live-screen`} target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #555', color: '#888', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>📺 LIVE</a>
            <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/warmup-screen`} target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #555', color: '#888', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🏋️ WARMUP</a>
            <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/protocol`} target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🖨️ PROTOCOL</a>
            <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/certificates`} target="_blank" style={{ padding: '8px 16px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>📜 CERTIFICATES</a>
            <button onClick={async () => { if (!confirm('Send emails?')) return; await api.post(`/competitions/${competitionId}/email-certificates`); alert('Sent!'); }} style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #333', color: '#666', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>📧 EMAIL ALL</button>
            <button onClick={togglePublish} style={{ padding: '8px 16px', background: competition.status === 'PUBLISHED' ? '#333' : '#4caf50', color: competition.status === 'PUBLISHED' ? '#888' : '#000', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>
              {competition.status === 'PUBLISHED' ? '🔒 UNPUBLISH' : '🌐 PUBLISH'}
            </button>
            <a href="https://ranking.worldstrongman.org/organizer/help" target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #333', color: '#555', borderRadius: '3px', fontSize: '11px', fontWeight: '700', letterSpacing: '1px', textDecoration: 'none' }}>📖 HELP</a>
          </div>
        </div>
      </div>
  <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch', scrollbarWidth: 'none', msOverflowStyle: 'none', marginBottom: '24px', borderBottom: '1px solid #1e1e1e' }}>
        <div style={{ display: 'flex', gap: '4px', minWidth: 'max-content' }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{ background: 'none', border: 'none', color: tab === t ? gold : '#555', padding: '10px 20px', cursor: 'pointer', fontSize: '13px', fontWeight: tab === t ? '700' : '400', borderBottom: tab === t ? `2px solid ${gold}` : '2px solid transparent', marginBottom: '-1px' }}>{t}</button>
        ))}
        </div>
      </div>

      {tab === 'Divisions' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
            <button onClick={() => setShowDivForm(!showDivForm)} style={{ padding: '8px 20px', background: showDivForm ? 'transparent' : gold, color: showDivForm ? gold : '#000', border: `1px solid ${gold}`, borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>{showDivForm ? 'CANCEL' : '+ ADD DIVISION'}</button>
          </div>
          {showDivForm && (
            <div style={{ background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '20px', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={labelStyle}>GENDER</label>
                  <select style={inputStyle} value={divForm._gender||''} onChange={e => {
                    const g = e.target.value;
                    const age = divForm._age||'SENIOR';
                    const weight = divForm._weight||'';
                    const key = weight ? `${g}_${age}_${weight}` : '';
                    setDivForm(f => ({ ...f, _gender: g, _age: age, _weight: '', division_key: key }));
                  }}>
                    <option value="">— Select —</option>
                    <option value="MEN">Men</option>
                    <option value="WOMEN">Women</option>
                    <option value="PARA_MEN">Para Men</option>
                    <option value="PARA_WOMEN">Para Women</option>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>AGE GROUP</label>
                  <select style={inputStyle} value={divForm._age||'SENIOR'} onChange={e => {
                    const age = e.target.value;
                    const g = divForm._gender||'';
                    const weight = divForm._weight||'';
                    const key = g && weight ? `${g}_${age}_${weight}` : '';
                    setDivForm(f => ({ ...f, _age: age, division_key: key }));
                  }}>
                    <option value="JUNIOR">Junior (U23)</option>
                    <option value="SENIOR">Senior (Open)</option>
                    <option value="MASTERS40">Masters 40+</option>
                    <option value="MASTERS50">Masters 50+</option>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>WEIGHT CLASS {divForm._gender ? '(' + divForm._gender + ')' : ''}</label>
                  <select key={divForm._gender||'none'} style={inputStyle} value={divForm._weight||''} onChange={e => {
                    const weight = e.target.value;
                    const g = divForm._gender||'';
                    const age = divForm._age||'SENIOR';
                    const key = g && weight ? g+'_'+age+'_'+weight : '';
                    setDivForm(f => ({ ...f, _weight: weight, division_key: key }));
                  }}>
                    <option value="">— Select —</option>
                    {(WEIGHT_OPTIONS[divForm._gender||'']||[]).map(([val,label]) => (
                      <option key={val} value={val}>{label}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={labelStyle}>FORMAT</label>
                  <select style={inputStyle} value={divForm.format} onChange={e => setDivForm(f => ({ ...f, format: e.target.value }))}>
                    <option value="CLASSIC">Classic</option>
                    <option value="RELAY">Relay</option>
                    <option value="TEAM_BATTLE">Team Battle</option>
                    <option value="PARA">Para</option>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>DIVISION KEY (AUTO)</label>
                  <input style={{...inputStyle, color: divForm.division_key ? '#4cc44c' : '#555'}}
                    value={divForm.division_key||''}
                    onChange={e => setDivForm(f => ({ ...f, division_key: e.target.value }))}
                    placeholder="Auto-generated or custom"
                  />
                </div>
              </div>
              <button onClick={async () => { await api.post('/divisions/', {...divForm, competition_id: competitionId}); await loadDivisions();
      const regRes = await api.get(`/competitions/${competitionId}/registrations`);
      setRegistrations(regRes.data); setShowDivForm(false); setDivForm({ division_key: '', format: 'Classic' }); }} style={{ marginTop: '16px', padding: '10px 24px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>CREATE DIVISION</button>
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {divisions.map(d => (
              <div key={d.id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div><div style={{ color: '#fff', fontWeight: '700', fontSize: '14px', letterSpacing: '1px' }}>{divisionLabel(d.division_key)}</div><div style={{ color: '#555', fontSize: '10px', letterSpacing: '2px' }}>{d.division_key}</div><div style={{ color: '#555', fontSize: '12px' }}>{d.format || 'Classic'}</div></div>
                <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => { setTab('Athletes'); selectDivision(d); }} style={{ padding: '6px 14px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>ATHLETES →</button>
                <button onClick={async () => {
                  const msg = d.status !== 'DRAFT' ? `Division is ${d.status} — cannot delete` : `Delete division ${d.division_key}?`;
                  if (d.status !== 'DRAFT') { alert(msg); return; }
                  if (!window.confirm(msg)) return;
                  try {
                    await api.delete(`/divisions/${d.id}`);
                    await loadDivisions();
                  } catch(e) { alert(e.response?.data?.detail || 'Cannot delete'); }
                }} style={{ padding: '6px 14px', background: 'transparent', border: '1px solid #4a2a2a', color: '#c44c4c', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>✕</button>
              </div>
              </div>
            ))}
            {divisions.length === 0 && <p style={{ color: '#444' }}>No divisions yet.</p>}
          </div>
        </div>
      )}

      {tab === 'Athletes' && (
        <div>
          <div style={{ marginBottom: '16px' }}>
            <label style={labelStyle}>Division</label>
            <select style={inputStyle} value={selectedDivision?.id || ''} onChange={e => { const d = divisions.find(x => x.id === e.target.value); if (d) selectDivision(d); }}>
              <option value="">Select division</option>
              {divisions.map(d => <option key={d.id} value={d.id}>{d.division_key}</option>)}
            </select>
          </div>
          {selectedDivision && (
            <div>
              <div style={{ marginBottom: '16px' }}>
                <label style={labelStyle}>Search athlete</label>
                <input style={inputStyle} placeholder="Type name..." value={athleteSearch} onChange={e => searchAthletes(e.target.value)} />
                {athleteResults.length > 0 && (
                  <div style={{ background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', marginTop: '4px' }}>
                    {athleteResults.map(a => (
                      <div key={a.id} style={{ padding: '10px 14px', borderBottom: '1px solid #1a1a1a', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ color: '#fff' }}>{a.first_name} {a.last_name}</span>
                        <span style={{ color: '#555', fontSize: '12px' }}>{a.country}</span>
                        <input placeholder="BIB" style={{ ...inputStyle, width: '70px', padding: '4px 8px' }} value={bibForm[a.id]||''} onChange={e => setBibForm({...bibForm, [a.id]: e.target.value})} />
                        <input placeholder="BW kg" style={{ ...inputStyle, width: '80px', padding: '4px 8px' }} value={bwForm[a.id]||''} onChange={e => setBwForm({...bwForm, [a.id]: e.target.value})} />
                        <button onClick={() => registerAthlete(a.id)} style={{ padding: '4px 14px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>+ ADD</button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <button onClick={() => setShowNewAthleteForm(!showNewAthleteForm)} style={{ marginBottom: '16px', padding: '8px 18px', background: 'transparent', border: '1px solid #333', color: '#666', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>+ CREATE NEW ATHLETE</button>
              {showNewAthleteForm && (
                <div style={{ background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '16px', marginBottom: '16px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                    {['first_name','last_name','country','email'].map(f => (
                      <div key={f}><label style={labelStyle}>{f.replace('_',' ').toUpperCase()}</label><input style={inputStyle} value={newAthlete[f]} onChange={e => setNewAthlete({...newAthlete, [f]: e.target.value})} /></div>
                    ))}
                  </div>
                  <button onClick={createAndRegister} style={{ padding: '8px 20px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>CREATE & REGISTER</button>
                </div>
              )}
              <div style={{ color: gold, fontSize: '10px', letterSpacing: '3px', marginBottom: '12px' }}>REGISTERED ({athletes.length})</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {athletes.map(a => (
                  <div key={a.id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span style={{ color: gold, fontSize: '16px', fontWeight: '900' }}>#{a.bib_no||'?'}</span>
                    <span style={{ color: '#fff', fontWeight: '600' }}>{a.first_name} {a.last_name}</span>
                    <button onClick={async () => {
                      if (!window.confirm('Remove athlete from division?')) return;
                      try {
                        await api.delete(`/athletes/participants/${a.id}`);
                        const res = await api.get(`/athletes/division/${selectedDivision.id}`);
                        setAthletes(res.data);
                      } catch(e) { alert(e.response?.data?.detail || 'Error'); }
                    }} style={{ marginLeft: 'auto', padding: '4px 10px', background: 'transparent', border: '1px solid #4a2a2a', color: '#c44c4c', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>✕</button>
                    <span style={{ color: '#555', fontSize: '12px' }}>{a.country}</span>
                    <span style={{ color: '#444', fontSize: '12px', marginLeft: 'auto' }}>{a.bodyweight_kg ? a.bodyweight_kg + ' kg' : ''}</span>
                  </div>
                ))}
                {athletes.length === 0 && <p style={{ color: '#444' }}>No athletes yet.</p>}
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'Disciplines' && <DisciplinesTab divisions={divisions} competitionId={competitionId} />}

  {tab === 'Start Order' && (
        <div>
          {!liveData ? <p style={{color:'#444'}}>Loading...</p> : (
            <div>
              <div style={{display:'flex', gap:'8px', marginBottom:'20px', flexWrap:'wrap'}}>
                {liveData.divisions.map((d,i) => (
                  <button key={d.division_id} onClick={() => { setSoDiv(i); setSoDisc(0); }} style={{padding:'8px 20px', background: soDiv===i ? gold : '#111', color: soDiv===i ? '#000' : '#555', border: `1px solid ${soDiv===i ? gold : '#222'}`, borderRadius:'3px', fontSize:'11px', fontWeight:'700', cursor:'pointer'}}>{d.division_name}</button>
                ))}
              </div>
              {liveData.divisions[soDiv] && (
                <div>
                  <div style={{display:'flex', gap:'8px', marginBottom:'16px', flexWrap:'wrap'}}>
                    {liveData.divisions[soDiv].disciplines.map((d,i) => (
                      <button key={d.id} onClick={() => setSoDisc(i)} style={{padding:'6px 14px', background:'transparent', color: soDisc===i ? gold : '#555', border: `1px solid ${soDisc===i ? gold : '#1a1a1a'}`, borderRadius:'3px', fontSize:'10px', cursor:'pointer'}}>{d.name}</button>
                    ))}
                  </div>
                  {liveData.divisions[soDiv].disciplines[soDisc] && (() => {
                    const div = liveData.divisions[soDiv];
                    const disc = div.disciplines[soDisc];
                    const ordered = [...div.participants].sort((a,b) => (disc.start_order[a.participant_id]||999) - (disc.start_order[b.participant_id]||999));
                    return (
                      <table style={{width:'100%', borderCollapse:'collapse'}}>
                        <thead><tr style={{borderBottom:'1px solid #1a1a1a'}}>{['#','LOT','BIB','ATHLETE','COUNTRY'].map(h => <th key={h} style={{padding:'8px 12px', textAlign:'left', fontSize:'9px', letterSpacing:'3px', color:'#444'}}>{h}</th>)}</tr></thead>
                        <tbody>
                          {ordered.map((p, idx) => (
                            <tr key={p.participant_id} style={{borderBottom:'1px solid #0d0d0d'}}>
                              <td style={{padding:'12px', color:gold, fontWeight:'900', fontSize:'20px'}}>{idx+1}</td>
                              <td style={{padding:'12px', color:'#555'}}>{p.lot_number||'—'}</td>
                              <td style={{padding:'12px', color:'#555'}}>#{p.bib_no||'—'}</td>
                              <td style={{padding:'12px', color:'#fff', fontWeight:'600'}}>{p.first_name} {p.last_name}</td>
                              <td style={{padding:'12px', color:'#555', fontSize:'12px'}}>{p.country||'—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    );
                  })()}
                  <div style={{marginTop:'24px', display:'flex', gap:'12px'}}>
                    <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/live-screen`} target="_blank" style={{padding:'10px 20px', background:'transparent', border:'1px solid #555', color:'#888', borderRadius:'3px', fontSize:'11px', fontWeight:'700', textDecoration:'none'}}>📺 OPEN LIVE SCREEN</a>
                    <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/warmup-screen`} target="_blank" style={{padding:'10px 20px', background:'transparent', border:'1px solid #555', color:'#888', borderRadius:'3px', fontSize:'11px', fontWeight:'700', textDecoration:'none'}}>🏋️ OPEN WARMUP SCREEN</a>
                    <button onClick={() => api.get(`/competitions/${competitionId}/live-data`).then(r => setLiveData(r.data))} style={{padding:'10px 20px', background:gold, border:'none', color:'#000', borderRadius:'3px', fontSize:'11px', fontWeight:'700', cursor:'pointer'}}>🔄 REFRESH</button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {tab === 'Protocol' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div style={{ color: gold, fontSize: '10px', letterSpacing: '3px' }}>COMPETITION PROTOCOL</div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/protocol`} target="_blank" style={{ padding: '8px 18px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🖨️ PRINT</a>
              <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/page`} target="_blank" style={{ padding: '8px 18px', background: 'transparent', border: '1px solid #333', color: '#888', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🌐 PUBLIC PAGE</a>
            </div>
          </div>
          {liveData && liveData.divisions.map(div => (
            <div key={div.division_id} style={{ marginBottom: '32px' }}>
              <div style={{ color: '#fff', fontSize: '13px', fontWeight: '700', letterSpacing: '3px', marginBottom: '12px', paddingBottom: '8px', borderBottom: `1px solid ${gold}` }}>{div.division_name}</div>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #1a1a1a' }}>
                      <th style={{ padding: '8px 10px', textAlign: 'left', color: '#444', fontSize: '9px' }}>PLACE</th>
                      <th style={{ padding: '8px 10px', textAlign: 'left', color: '#444', fontSize: '9px' }}>ATHLETE</th>
                      <th style={{ padding: '8px 10px', textAlign: 'left', color: '#444', fontSize: '9px' }}>COUNTRY</th>
                      {div.disciplines.map(d => <th key={d.id} style={{ padding: '8px 10px', textAlign: 'center', color: '#444', fontSize: '9px' }}>{d.name}</th>)}
                      <th style={{ padding: '8px 10px', textAlign: 'center', color: '#444', fontSize: '9px' }}>TOTAL</th>
                    </tr>
                  </thead>
                  <tbody>
                    {div.participants.map((p, idx) => {
                      const total = div.disciplines.reduce((sum, d) => sum + (parseFloat(d.results[p.participant_id]) || 0), 0);
                      return (
                        <tr key={p.participant_id} style={{ borderBottom: '1px solid #0d0d0d' }}>
                          <td style={{ padding: '10px', color: gold, fontWeight: '900', fontSize: '18px' }}>{idx+1}</td>
                          <td style={{ padding: '10px', color: '#fff', fontWeight: '600' }}>{p.first_name} {p.last_name}</td>
                          <td style={{ padding: '10px', color: '#555', fontSize: '12px' }}>{p.country||'-'}</td>
                          {div.disciplines.map(d => <td key={d.id} style={{ padding: '10px', textAlign: 'center', color: '#888' }}>{d.results[p.participant_id]||'-'}</td>)}
                          <td style={{ padding: '10px', textAlign: 'center', color: gold, fontWeight: '700' }}>{total ? total.toFixed(1) : '-'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'Judges' && (
        <div>
          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>Search Judge</label>
            <input style={inputStyle} placeholder="Type name..." value={judgeSearch} onChange={e => searchJudges(e.target.value)} />
            {judgeResults.length > 0 && (
              <div style={{ background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', marginTop: '4px' }}>
                {judgeResults.map(j => (
                  <div key={j.id} onClick={() => { setSelectedJudge(j); setJudgeSearch(j.first_name + ' ' + j.last_name); setJudgeResults([]); }} style={{ padding: '10px 14px', cursor: 'pointer', borderBottom: '1px solid #1a1a1a', color: '#fff' }}>
                    {j.first_name} {j.last_name} <span style={{ color: '#555', fontSize: '12px' }}>· {j.country||'—'}</span>
                  </div>
                ))}
              </div>
            )}
            {selectedJudge && (
              <div style={{ marginTop: '12px', background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '16px' }}>
                <div style={{ color: gold, fontSize: '13px', marginBottom: '12px' }}>✓ {selectedJudge.first_name} {selectedJudge.last_name}</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '12px', alignItems: 'end' }}>
                  <div><label style={labelStyle}>Role</label>
                    <select style={inputStyle} value={judgeRole} onChange={e => setJudgeRole(e.target.value)}>
                      <option value="Head Judge">Head Judge</option>
                      <option value="Judge">Judge</option>
                      <option value="Technical Delegate">Technical Delegate</option>
                      <option value="Referee">Referee</option>
                    </select>
                  </div>
                  <button onClick={assignJudge} style={{ padding: '11px 24px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>ASSIGN →</button>
                </div>
              </div>
            )}
          </div>
          <div style={{ color: gold, fontSize: '10px', letterSpacing: '3px', marginBottom: '12px' }}>ASSIGNED JUDGES ({judges.length})</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {judges.map(j => (
              <div key={j.id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ background: 'rgba(201,168,76,0.1)', color: gold, fontSize: '10px', fontWeight: '700', padding: '3px 8px', borderRadius: '2px' }}>{j.role}</div>
                  <div><div style={{ color: '#fff', fontWeight: '600' }}>{j.first_name} {j.last_name}</div><div style={{ color: '#555', fontSize: '12px' }}>{j.country||'—'}</div></div>
                </div>
                <button onClick={() => removeJudge(j.id)} style={{ background: 'transparent', border: '1px solid #2a2a2a', color: '#555', padding: '4px 10px', borderRadius: '3px', cursor: 'pointer', fontSize: '11px' }}>Remove</button>
              </div>
            ))}
            {judges.length === 0 && (<p style={{ color: '#444' }}>No judges assigned yet.</p>)}
          </div>
        </div>
      )}
      {tab === 'Draw' && (
        <DrawTab competitionId={competitionId} divisions={divisions} />
      )}

      {tab === 'MC' && <MCTab competitionId={competitionId} competition={competition} />}
      {tab === 'Registrations' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div style={{ color: gold, fontSize: '10px', letterSpacing: '3px' }}>APPLICATIONS ({registrations.length})</div>
            <button onClick={async () => { const res = await api.get(`/competitions/${competitionId}/registrations`); setRegistrations(res.data); }} style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #333', color: '#666', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>🔄 REFRESH</button>
          </div>
          {registrations.length === 0 && <p style={{ color: '#444' }}>No applications yet.</p>}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {registrations.map(r => (
              <div key={r.id} style={{ background: '#111', border: `1px solid ${r.status === 'PAID' ? '#1a4a1a' : r.status === 'PENDING' ? '#333' : r.status === 'ACCEPTED' ? '#2a4a2a' : '#4a2a2a'}`, borderRadius: '4px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
                    <span style={{ color: r.status === 'PAID' ? '#4cc44c' : r.status === 'PENDING' ? gold : r.status === 'ACCEPTED' ? '#4caf50' : '#f44336', fontSize: '10px', fontWeight: '700', letterSpacing: '2px' }}>{r.status}</span>
                    <span style={{ color: '#fff', fontWeight: '600' }}>{r.athlete_name}</span>
                    <span style={{ color: '#555', fontSize: '12px' }}>{r.country}</span>
                    <span style={{ color: gold, fontSize: '12px' }}>{r.division_key}</span>
                  </div>
                  <div style={{ color: '#444', fontSize: '11px' }}>{r.athlete_email} · {r.payment_method === 'crypto' ? '₿ USDT' : '💳 Card'} · <span style={{color: r.status === 'PAID' ? '#4cc44c' : '#c9a84c'}}>€{r.amount_eur}</span>{r.coupon_code && <span style={{color:'#2ab8b8', marginLeft:'8px'}}>🏷️ {r.coupon_code}</span>}</div>
                  <div style={{ color: '#333', fontSize: '10px', marginTop: '2px' }}>{r.created_at ? new Date(r.created_at).toLocaleString() : ''}</div>
                </div>
                {r.status === 'PENDING' && (
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={async () => { await api.patch(`/competitions/${competitionId}/registrations/${r.id}`, { status: 'ACCEPTED' }); const res = await api.get(`/competitions/${competitionId}/registrations`); setRegistrations(res.data); }} style={{ padding: '8px 16px', background: '#2a4a2a', border: '1px solid #4caf50', color: '#4caf50', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>✓ ACCEPT</button>
                    <button onClick={async () => { const reason = prompt('Reject reason (optional):'); await api.patch(`/competitions/${competitionId}/registrations/${r.id}`, { status: 'REJECTED', reject_reason: reason || '' }); const res = await api.get(`/competitions/${competitionId}/registrations`); setRegistrations(res.data); }} style={{ padding: '8px 16px', background: '#4a2a2a', border: '1px solid #f44336', color: '#f44336', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>✕ REJECT</button>
                  </div>
                )}
                {r.status === 'PAID' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', minWidth: '160px' }}>
                    <select
                      id={`div-select-${r.id}`}
                      style={{ padding: '6px 10px', background: '#0a0a0a', border: '1px solid #2a2a2a', color: '#fff', borderRadius: '3px', fontSize: '11px' }}
                      defaultValue=""
                    >
                      <option value="">Select division...</option>
                      {divisions.map(d => <option key={d.id} value={d.id}>{d.division_key}</option>)}
                    </select>
                    <button onClick={async () => {
                      const divId = document.getElementById(`div-select-${r.id}`).value;
                      if (!divId) { alert('Select a division first'); return; }
                      try {
                        await api.post('/athletes/register', { competition_division_id: divId, athlete_id: r.athlete_id });
                        alert('✅ Athlete added to division!');
                      } catch(e) { alert(e.response?.data?.detail || 'Error adding athlete'); }
                    }} style={{ padding: '6px 12px', background: '#1a3a1a', border: '1px solid #4cc44c', color: '#4cc44c', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>
                      ➕ ADD TO DIVISION
                    </button>
                  </div>
                )}
                {r.status !== 'PENDING' && r.reject_reason && (
                  <div style={{ color: '#f44336', fontSize: '11px' }}>{r.reject_reason}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="wsm-banner-wrap" style={{ marginTop: '32px', background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '20px', marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {competition.banner_url
          ? <img src={competition.banner_url?.startsWith('http') ? competition.banner_url : `https://ranking.worldstrongman.org${competition.banner_url}`} style={{ width: '100%', maxWidth: '300px', height: '120px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #2a2a2a' }} />
          : <div style={{ width: '100%', maxWidth: '300px', height: '120px', background: '#0a0a0a', border: '1px dashed #333', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#333', fontSize: '12px' }}>No banner</div>
        }
        <div style={{ flex: '1', minWidth: '200px' }}>
          <div style={{ color: '#888', fontSize: '11px', letterSpacing: '2px', marginBottom: '8px' }}>COMPETITION BANNER</div>
          <label style={{ padding: '10px 20px', background: gold, color: '#000', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', display: 'inline-block' }}>
            🖼️ {bannerUploading ? 'UPLOADING...' : 'UPLOAD BANNER'}
            <input type="file" accept=".jpg,.jpeg,.png,.webp" style={{ display: 'none' }} onChange={e => e.target.files[0] && uploadBanner(e.target.files[0])} />
          </label>
          <div style={{ color: '#444', fontSize: '11px', marginTop: '6px' }}>Recommended: 1500×640px · JPG/PNG · max 2MB</div>
        </div>
      </div>

      <div style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '20px', marginBottom: '20px' }}>
        <div style={{ color: gold, fontSize: '10px', letterSpacing: '3px', marginBottom: '16px' }}>SPONSORS ({sponsors.length}/6)</div>
        {sponsors.map(s => (
          <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 0', borderBottom: '1px solid #1a1a1a' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              {s.logo_url ? <img src={s.logo_url?.startsWith("http") ? s.logo_url : `https://ranking.worldstrongman.org${s.logo_url}`} style={{ width: '80px', height: '50px', objectFit: 'contain', background: '#1a1a1a', borderRadius: '4px' }} /> : <div style={{ width: '80px', height: '50px', background: '#1a1a1a', border: '1px dashed #333', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#444' }}>🎽</div>}
              <label style={{ padding: '3px 8px', border: `1px solid ${gold}`, color: gold, fontSize: '9px', fontWeight: '700', cursor: 'pointer', borderRadius: '2px' }}>
                📷 LOGO
                <input type="file" accept=".jpg,.jpeg,.png,.webp" style={{ display: 'none' }} onChange={async e => { if (!e.target.files[0]) return; const fd = new FormData(); fd.append('file', e.target.files[0]); const res = await api.post(`/competitions/${competitionId}/sponsors/${s.id}/logo`, fd); setSponsors(sponsors.map(sp => sp.id === s.id ? {...sp, logo_url: res.data.logo_url} : sp)); }} />
              </label>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span style={{ color: s.tier === 'PAID' ? gold : '#888', fontSize: '10px', fontWeight: '700', background: s.tier === 'PAID' ? 'rgba(201,168,76,0.1)' : '#1a1a1a', padding: '2px 6px', borderRadius: '2px' }}>{s.tier}</span>
                <span style={{ color: '#fff', fontSize: '14px', fontWeight: '600' }}>{s.name}</span>
              </div>
              {s.website_url && <a href={s.website_url} target="_blank" style={{ color: '#555', fontSize: '11px', textDecoration: 'none' }}>{s.website_url}</a>}
            </div>
            <button onClick={() => deleteSponsor(s.id)} style={{ background: 'transparent', border: '1px solid #333', color: '#666', padding: '3px 8px', borderRadius: '3px', cursor: 'pointer', fontSize: '11px' }}>✕</button>
          </div>
        ))}
        {sponsors.length < 6 && (
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end', marginTop: '16px', flexWrap: 'wrap' }}>
            <div style={{ flex: 2 }}><label style={labelStyle}>NAME</label><input value={newSponsor.name} onChange={e => setNewSponsor({...newSponsor, name: e.target.value})} placeholder="Sponsor name" style={inputStyle} /></div>
            <div style={{ flex: 2 }}><label style={labelStyle}>WEBSITE</label><input value={newSponsor.website_url} onChange={e => setNewSponsor({...newSponsor, website_url: e.target.value})} placeholder="https://..." style={inputStyle} /></div>
            <div style={{ flex: 1 }}><label style={labelStyle}>TYPE</label><select value={newSponsor.tier} onChange={e => setNewSponsor({...newSponsor, tier: e.target.value})} style={inputStyle}><option value="FREE">FREE</option><option value="PAID">PAID</option></select></div>
            <button onClick={addSponsor} style={{ padding: '10px 16px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>+ ADD</button>
          </div>
        )}
      </div>

      <div style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '24px', marginBottom: '24px' }}>
        <div style={{ color: gold, fontSize: '10px', letterSpacing: '3px', marginBottom: '16px' }}>COMPETITION INFO</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          {[['name','NAME'],['city','CITY'],['country','COUNTRY'],['organizer_email','ORGANIZER EMAIL'],['date_start','DATE START'],['date_end','DATE END']].map(([field, label]) => (
            <div key={field}><label style={labelStyle}>{label}</label><input style={inputStyle} value={editForm[field]||''} onChange={e => setEditForm({...editForm, [field]: e.target.value})} /></div>
          ))}
        </div>
        
        {/* ENTRY FEE SECTION */}
        <div style={{ marginTop: '24px', padding: '16px', background: '#0d1a0d', border: '1px solid #1a3a1a', borderRadius: '6px' }}>
          <div style={{ color: '#4cc44c', fontSize: '10px', letterSpacing: '3px', marginBottom: '14px' }}>💰 ENTRY FEE SETTINGS</div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <input 
              type="checkbox" 
              id="entry_fee_enabled"
              checked={editForm.entry_fee_enabled||false} 
              onChange={e => setEditForm({...editForm, entry_fee_enabled: e.target.checked})}
              style={{ width: '16px', height: '16px', cursor: 'pointer' }}
            />
            <label htmlFor="entry_fee_enabled" style={{ color: '#aaa', fontSize: '12px', cursor: 'pointer', letterSpacing: '1px' }}>
              Enable Entry Fee for this competition
            </label>
          </div>

          {editForm.entry_fee_enabled && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={labelStyle}>ENTRY FEE (EUR)</label>
                <input 
                  type="number" 
                  min="0" 
                  step="0.01"
                  style={inputStyle} 
                  value={editForm.entry_fee||''} 
                  onChange={e => setEditForm({...editForm, entry_fee: e.target.value})}
                  placeholder="e.g. 30"
                />
              </div>
              <div>
                <label style={labelStyle}>REGISTRATION DEADLINE</label>
                <input 
                  type="date" 
                  style={inputStyle} 
                  value={editForm.registration_deadline||''} 
                  onChange={e => setEditForm({...editForm, registration_deadline: e.target.value})}
                />
              </div>
              <div style={{ gridColumn: '1/-1', display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', background: '#1a0a0a', borderRadius: '4px', border: '1px solid #3a1a1a' }}>
                <input 
                  type="checkbox" 
                  id="non_refundable"
                  checked={editForm.entry_fee_non_refundable !== false} 
                  onChange={e => setEditForm({...editForm, entry_fee_non_refundable: e.target.checked})}
                  style={{ width: '14px', height: '14px' }}
                />
                <label htmlFor="non_refundable" style={{ color: '#c44c4c', fontSize: '11px', letterSpacing: '1px', cursor: 'pointer' }}>
                  ⚠️ Entry fee is NON-REFUNDABLE — athlete confirms at registration
                </label>
              </div>
              <div style={{ gridColumn: '1/-1', padding: '10px', background: '#0a1a0a', borderRadius: '4px', fontSize: '11px', color: '#666' }}>
                💰 WSM Commission: <span style={{color:'#c9a84c'}}>15%</span> &nbsp;·&nbsp; 
                Organizer payout: <span style={{color:'#4cc44c'}}>85%</span> &nbsp;·&nbsp;
                Payout after registration deadline
              </div>
            </div>
          )}
        </div>

        
<button onClick={saveCompetition} disabled={saving} style={{ marginTop: '16px', padding: '10px 24px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', letterSpacing: '1px' }}>
          {saving ? 'SAVING...' : 'SAVE CHANGES →'}
        </button>
      </div>
    </Layout>
  );
}
