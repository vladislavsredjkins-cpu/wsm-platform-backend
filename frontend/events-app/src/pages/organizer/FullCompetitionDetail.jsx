import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import api from '../../api';
import Layout from '../../components/Layout';
import DisciplinesTab from '../../components/DisciplinesTab';
import DrawTab from '../../components/DrawTab';
import MCTab from '../../components/MCTab';
import { divisionLabel } from '../../constants/divisions';

const inputStyle = { width: '100%', padding: '10px 14px', background: '#fff', border: '1px solid #e8e0d0', color: '#1a1a1a', borderRadius: '3px', fontSize: '13px', outline: 'none' };
const labelStyle = { display: 'block', color: '#777', fontSize: '10px', letterSpacing: '2px', marginBottom: '6px' };
const TABS = ['Divisions', 'Athletes', 'Disciplines', 'Judges', 'Draw', 'Start Order', 'Protocol', 'MC', 'Registrations'];

export default function CompetitionDetail() {
  const { competitionId } = useParams();
  const API = 'https://api.events.worldstrongman.org';
  const authCfg = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });
  const [competition, setCompetition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('Divisions');
  const [divisions, setDivisions] = useState([]);
  const [showDivForm, setShowDivForm] = useState(false);
  const [divForm, setDivForm] = useState({ name: '', gender: 'male', weight_min: '', weight_max: '', age_group: 'open', format: 'individual', sport_type: 'strongman' });
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
  const [inviteForm, setInviteForm] = useState({ email: '', name: '' });
  const [sendingInvite, setSendingInvite] = useState(false);
  const [lastInviteLink, setLastInviteLink] = useState(null);
  const [sponsors, setSponsors] = useState([]);
  const [newSponsor, setNewSponsor] = useState({ name: '', website_url: '', tier: 'FREE' });
  const [bannerUploading, setBannerUploading] = useState(false);
  const [editForm, setEditForm] = useState({ name: '', city: '', country: '', organizer_email: '', date_start: '', date_end: '', entry_fee_enabled: false, entry_fee: '', registration_deadline: '', entry_fee_non_refundable: true });
  const [saving, setSaving] = useState(false);
  const [liveData, setLiveData] = useState(null);
  const [soDiv, setSoDiv] = useState(0);
  const [soParticipants, setSoParticipants] = useState([]);
  const [soLoading, setSoLoading] = useState(false);
  const [registrations, setRegistrations] = useState([]);

  const loadDivisions = useCallback(() => {
    return api.get(`/divisions/${competitionId}`).then(r => setDivisions(r.data));
  }, [competitionId]);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/competitions/${competitionId}`, authCfg()).then(r => {
        setCompetition(r.data);
        setEditForm({ name: r.data.name, city: r.data.city||'', country: r.data.country||'', organizer_email: r.data.organizer_email||'', date_start: r.data.date_start||'', date_end: r.data.date_end||'', entry_fee_enabled: r.data.entry_fee_enabled||false, entry_fee: r.data.entry_fee||'', registration_deadline: r.data.registration_deadline||'', entry_fee_non_refundable: r.data.entry_fee_non_refundable !== false });
      }),
      api.get(`/judges/invites/${competitionId}`).then(r => setJudges(r.data)),
      // axios.get(`${API}/competitions/${competitionId}/sponsors`, authCfg()).then(r => setSponsors(r.data)),
      // axios.get(`${API}/competitions/${competitionId}/live-data`, authCfg()).then(r => setLiveData(r.data)),
      loadDivisions(),
    ]).finally(() => setLoading(false));
  }, [competitionId, loadDivisions]);

  const selectDivision = async (div) => {
    setSelectedDivision(div);
    const res = await api.get(`/participants/competition/${competitionId}`);
    setAthletes(res.data.filter(p => p.events_division_id === div.id));
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
      await api.post(`/participants/`, {
        athlete_id: athleteId,
        events_division_id: selectedDivision.id,
        competition_id: competitionId,
        bib_no: parseInt(bibForm[athleteId]) || null,
        bodyweight_kg: parseFloat(bwForm[athleteId]) || null,
      });
      const res = await api.get(`/participants/competition/${competitionId}`);
      setAthletes(res.data.filter(p => p.events_division_id === selectedDivision.id));
      setAthleteSearch(''); setAthleteResults([]);
    } catch(e) { alert(e.response?.data?.detail || 'Error'); }
    finally { setSavingAthlete(false); }
  };

  const createAndRegister = async () => {
    setSavingAthlete(true);
    try {
      await api.post('/participants/', {
        ...newAthlete,
        events_division_id: selectedDivision.id,
        competition_id: competitionId,
      });
      const res = await api.get(`/participants/competition/${competitionId}`);
      setAthletes(res.data.filter(p => p.events_division_id === selectedDivision.id));
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
      const res = await axios.patch(`${API}/competitions/${competitionId}`, formToSave, authCfg());
      setCompetition(res.data);
    } finally { setSaving(false); }
  };

  const togglePublish = async () => {
    const action = competition.status === 'PUBLISHED' ? 'unpublish' : 'publish';
    const res = await axios.patch(`${API}/competitions/${competitionId}/${action}`, {}, authCfg());
    setCompetition(res.data);
  };

  const uploadBanner = async (file) => {
    setBannerUploading(true);
    try {
      const fd = new FormData(); fd.append('file', file);
      const res = await axios.post(`${API}/competitions/${competitionId}/banner`, fd, authCfg());
      setCompetition(prev => ({ ...prev, banner_url: res.data.banner_url }));
    } finally { setBannerUploading(false); }
  };

  const addSponsor = async () => {
    if (!newSponsor.name.trim()) return;
    const res = await axios.post(`${API}/competitions/${competitionId}/sponsors`, newSponsor, authCfg());
    setSponsors([...sponsors, res.data]);
    setNewSponsor({ name: '', website_url: '', tier: 'FREE' });
  };

  const deleteSponsor = async (sid) => {
    await axios.delete(`${API}/competitions/${competitionId}/sponsors/${sid}`, authCfg());
    setSponsors(sponsors.filter(s => s.id !== sid));
  };

  const sendInvite = async () => {
    if (!inviteForm.name) return alert('Name is required');
    setSendingInvite(true);
    setLastInviteLink(null);
    try {
      const inv = await api.post(`/judges/invite`, { competition_id: competitionId, email: inviteForm.email, name: inviteForm.name });
      const link = `https://events.worldstrongman.org/judge/${inv.data.token}`;
      setLastInviteLink(link);
      const res = await api.get(`/judges/invites/${competitionId}`);
      setJudges(res.data);
      setInviteForm({ email: '', name: '' });
    } catch(e) { alert(e.response?.data?.detail || 'Failed to generate invite'); }
    finally { setSendingInvite(false); }
  };

  const loadStartOrder = async (divId) => {
    setSoLoading(true);
    try {
      const res = await api.get(`/competitions/${competitionId}/divisions/${divId}/draw`);
      setSoParticipants(res.data);
    } catch { setSoParticipants([]); }
    finally { setSoLoading(false); }
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
            <h1 style={{ color: '#1a1a1a', fontSize: '28px', fontWeight: '900', letterSpacing: '3px', margin: 0 }}>{competition.name}</h1>
            <div style={{ color: '#555', fontSize: '12px', letterSpacing: '2px', marginTop: '4px' }}>{competition.date_start} · {competition.city} · {competition.country}</div>
          </div>
  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            
            <button onClick={() => setTab('Draw')} style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #005B5C', color: '#005B5C', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>🎲 DRAW</button>
            <a href={`https://api.events.worldstrongman.org/competitions/${competitionId}/live-screen`} target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #bbb', color: '#888', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>📺 LIVE</a>
            <a href={`https://api.events.worldstrongman.org/competitions/${competitionId}/warmup-screen`} target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #bbb', color: '#888', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🏋️ WARMUP</a>
            <a href={`https://api.events.worldstrongman.org/competitions/${competitionId}/protocol`} target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #005B5C', color: '#005B5C', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🖨️ PROTOCOL</a>
            <a href={`https://api.events.worldstrongman.org/competitions/${competitionId}/certificates`} target="_blank" style={{ padding: '8px 16px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>📜 CERTIFICATES</a>
            <button onClick={async () => { if (!confirm('Send emails?')) return; await axios.post(`${API}/competitions/${competitionId}/email-certificates`, {}, authCfg()); alert('Sent!'); }} style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #e8e0d0', color: '#888', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>📧 EMAIL ALL</button>
            <button onClick={togglePublish} style={{ padding: '8px 16px', background: competition.status === 'PUBLISHED' ? '#f0ebe3' : '#4caf50', color: competition.status === 'PUBLISHED' ? '#888' : '#fff', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>
              {competition.status === 'PUBLISHED' ? '🔒 UNPUBLISH' : '🌐 PUBLISH'}
            </button>
            <a href="https://api.events.worldstrongman.org/organizer/help" target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #e8e0d0', color: '#888', borderRadius: '3px', fontSize: '11px', fontWeight: '700', letterSpacing: '1px', textDecoration: 'none' }}>📖 HELP</a>
          </div>
        </div>
      </div>
  <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch', scrollbarWidth: 'none', msOverflowStyle: 'none', marginBottom: '24px', borderBottom: '1px solid #e8e0d0' }}>
        <div style={{ display: 'flex', gap: '4px', minWidth: 'max-content' }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{ background: 'none', border: 'none', color: tab === t ? '#005B5C' : '#888', padding: '10px 20px', cursor: 'pointer', fontSize: '13px', fontWeight: tab === t ? '700' : '400', borderBottom: tab === t ? '2px solid #005B5C' : '2px solid transparent', marginBottom: '-1px' }}>{t}</button>
        ))}
        </div>
      </div>

      {tab === 'Divisions' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
            <button onClick={() => setShowDivForm(!showDivForm)} style={{ padding: '8px 20px', background: showDivForm ? 'transparent' : '#005B5C', color: showDivForm ? '#005B5C' : '#fff', border: '1px solid #005B5C', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>{showDivForm ? 'CANCEL' : '+ ADD DIVISION'}</button>
          </div>
          {showDivForm && (
            <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '20px', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <div style={{ gridColumn: '1 / -1' }}>
                  <label style={labelStyle}>DIVISION NAME</label>
                  <input style={inputStyle} placeholder="e.g. Men Open 105kg" value={divForm.name} onChange={e => setDivForm(f => ({ ...f, name: e.target.value }))} />
                </div>
                <div>
                  <label style={labelStyle}>GENDER</label>
                  <select style={inputStyle} value={divForm.gender} onChange={e => setDivForm(f => ({ ...f, gender: e.target.value }))}>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="mixed">Mixed</option>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>AGE GROUP</label>
                  <select style={inputStyle} value={divForm.age_group} onChange={e => setDivForm(f => ({ ...f, age_group: e.target.value }))}>
                    <option value="open">Open</option>
                    <option value="junior">Junior</option>
                    <option value="master">Master</option>
                    <option value="master50">Master 50+</option>
                    <option value="youth">Youth</option>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>WEIGHT MIN (KG)</label>
                  <input style={inputStyle} type="number" placeholder="0" value={divForm.weight_min} onChange={e => setDivForm(f => ({ ...f, weight_min: e.target.value }))} />
                </div>
                <div>
                  <label style={labelStyle}>WEIGHT MAX (KG)</label>
                  <input style={inputStyle} type="number" placeholder="999" value={divForm.weight_max} onChange={e => setDivForm(f => ({ ...f, weight_max: e.target.value }))} />
                </div>
                <div>
                  <label style={labelStyle}>FORMAT</label>
                  <select style={inputStyle} value={divForm.format} onChange={e => setDivForm(f => ({ ...f, format: e.target.value }))}>
                    <option value="individual">Individual</option>
                    <option value="relay">Relay</option>
                    <option value="team">Team</option>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>SPORT TYPE</label>
                  <select style={inputStyle} value={divForm.sport_type} onChange={e => setDivForm(f => ({ ...f, sport_type: e.target.value }))}>
                    <option value="strongman">Strongman</option>
                    <option value="strict_curl">Strict Curl</option>
                    <option value="stick_pulling">Stick Pulling</option>
                    <option value="powerlifting">Powerlifting</option>
                  </select>
                </div>
              </div>
              <button onClick={async () => {
                if (!divForm.name.trim()) { alert('Division name is required'); return; }
                await api.post('/divisions/', { ...divForm, competition_id: competitionId, weight_min: divForm.weight_min ? parseFloat(divForm.weight_min) : null, weight_max: divForm.weight_max ? parseFloat(divForm.weight_max) : null });
                await loadDivisions();
                const regRes = await axios.get(`${API}/competitions/${competitionId}/registrations`, authCfg());
                setRegistrations(regRes.data);
                setShowDivForm(false);
                setDivForm({ name: '', gender: 'male', weight_min: '', weight_max: '', age_group: 'open', format: 'individual', sport_type: 'strongman' });
              }} style={{ marginTop: '16px', padding: '10px 24px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>CREATE DIVISION</button>
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {divisions.map(d => (
              <div key={d.id} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div><div style={{ color: '#1a1a1a', fontWeight: '700', fontSize: '14px', letterSpacing: '1px' }}>{d.name || divisionLabel(d.division_key)}</div><div style={{ color: '#888', fontSize: '11px', marginTop: '2px' }}>{[d.gender, d.age_group, d.weight_min && d.weight_max ? `${d.weight_min}–${d.weight_max}kg` : null, d.sport_type].filter(Boolean).join(' · ')}</div><div style={{ color: '#aaa', fontSize: '11px' }}>{d.format}</div></div>
                <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => { setTab('Athletes'); selectDivision(d); }} style={{ padding: '6px 14px', background: 'transparent', border: '1px solid #005B5C', color: '#005B5C', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>ATHLETES →</button>
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
            {divisions.length === 0 && <p style={{ color: '#888' }}>No divisions yet.</p>}
          </div>
        </div>
      )}

      {tab === 'Athletes' && (
        <div>
          <div style={{ marginBottom: '16px' }}>
            <label style={labelStyle}>Division</label>
            <select style={inputStyle} value={selectedDivision?.id || ''} onChange={e => { const d = divisions.find(x => x.id === e.target.value); if (d) selectDivision(d); }}>
              <option value="">Select division</option>
              {divisions.map(d => <option key={d.id} value={d.id}>{d.name || d.division_key}</option>)}
            </select>
          </div>
          {selectedDivision && (
            <div>
              <div style={{ marginBottom: '16px' }}>
                <label style={labelStyle}>Search athlete</label>
                <input style={inputStyle} placeholder="Type name..." value={athleteSearch} onChange={e => searchAthletes(e.target.value)} />
                {athleteResults.length > 0 && (
                  <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '3px', marginTop: '4px' }}>
                    {athleteResults.map(a => (
                      <div key={a.id} style={{ padding: '10px 14px', borderBottom: '1px solid #f0ebe3', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ color: '#1a1a1a' }}>{a.first_name} {a.last_name}</span>
                        <span style={{ color: '#888', fontSize: '12px' }}>{a.country}</span>
                        <input placeholder="BIB" style={{ ...inputStyle, width: '70px', padding: '4px 8px' }} value={bibForm[a.id]||''} onChange={e => setBibForm({...bibForm, [a.id]: e.target.value})} />
                        <input placeholder="BW kg" style={{ ...inputStyle, width: '80px', padding: '4px 8px' }} value={bwForm[a.id]||''} onChange={e => setBwForm({...bwForm, [a.id]: e.target.value})} />
                        <button onClick={() => registerAthlete(a.id)} style={{ padding: '4px 14px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>+ ADD</button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <button onClick={() => setShowNewAthleteForm(!showNewAthleteForm)} style={{ marginBottom: '16px', padding: '8px 18px', background: 'transparent', border: '1px solid #333', color: '#666', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>+ CREATE NEW ATHLETE</button>
              {showNewAthleteForm && (
                <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '16px', marginBottom: '16px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                    {['first_name','last_name','country','email'].map(f => (
                      <div key={f}><label style={labelStyle}>{f.replace('_',' ').toUpperCase()}</label><input style={inputStyle} value={newAthlete[f]} onChange={e => setNewAthlete({...newAthlete, [f]: e.target.value})} /></div>
                    ))}
                  </div>
                  <button onClick={createAndRegister} style={{ padding: '8px 20px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>CREATE & REGISTER</button>
                </div>
              )}
              <div style={{ color: '#005B5C', fontSize: '10px', letterSpacing: '3px', marginBottom: '12px' }}>REGISTERED ({athletes.length})</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {athletes.map(a => (
                  <div key={a.id} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span style={{ color: '#005B5C', fontSize: '16px', fontWeight: '900' }}>#{a.bib_no||'?'}</span>
                    <span style={{ color: '#1a1a1a', fontWeight: '600' }}>{a.first_name} {a.last_name}</span>
                    <span style={{ color: '#888', fontSize: '12px' }}>{a.country}</span>
                    <span style={{ color: '#888', fontSize: '12px' }}>{a.bodyweight_kg ? a.bodyweight_kg + ' kg' : ''}</span>
                    {a.status === 'pending' && (
                      <button onClick={async () => {
                        try {
                          await api.patch(`/participants/${a.id}/status`, { status: 'confirmed' });
                          const res = await api.get(`/participants/competition/${competitionId}`);
                          setAthletes(res.data.filter(p => p.events_division_id === selectedDivision.id));
                        } catch(e) { alert(e.response?.data?.detail || 'Error'); }
                      }} style={{ marginLeft: 'auto', padding: '4px 12px', background: '#005B5C', border: 'none', color: '#fff', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>✓ Confirm</button>
                    )}
                    <button onClick={async () => {
                      if (!window.confirm('Remove athlete from division?')) return;
                      try {
                        await api.delete(`/participants/${a.id}`);
                        const res = await api.get(`/participants/competition/${competitionId}`);
                        setAthletes(res.data.filter(p => p.events_division_id === selectedDivision.id));
                      } catch(e) { alert(e.response?.data?.detail || 'Error'); }
                    }} style={{ padding: '4px 10px', background: 'transparent', border: '1px solid #ffcdd2', color: '#c44c4c', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>✕</button>
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
          {divisions.length === 0 ? (
            <p style={{ color: '#888' }}>No divisions yet. Add divisions first.</p>
          ) : (
            <div>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
                {divisions.map((d, i) => (
                  <button key={d.id} onClick={() => { setSoDiv(i); loadStartOrder(d.id); }}
                    style={{ padding: '8px 20px', background: soDiv === i ? '#005B5C' : '#fff', color: soDiv === i ? '#fff' : '#888', border: `1px solid ${soDiv === i ? '#005B5C' : '#e8e0d0'}`, borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>
                    {d.name || d.division_key}
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ color: '#005B5C', fontSize: '10px', letterSpacing: '3px' }}>START ORDER — {divisions[soDiv]?.name || divisions[soDiv]?.division_key}</div>
                <button onClick={() => loadStartOrder(divisions[soDiv]?.id)} style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #e8e0d0', color: '#555', borderRadius: '3px', fontSize: '11px', fontWeight: '600', cursor: 'pointer' }}>🔄 REFRESH</button>
              </div>

              {soLoading ? <p style={{ color: '#888' }}>Loading...</p> : (
                <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', overflow: 'hidden' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #e8e0d0', background: '#fafafa' }}>
                        {['#', 'LOT', 'BIB', 'ATHLETE', 'COUNTRY'].map(h => (
                          <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: '9px', letterSpacing: '3px', color: '#888', fontWeight: '700' }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[...soParticipants].sort((a, b) => (a.lot_number || 999) - (b.lot_number || 999)).map((p, idx) => (
                        <tr key={p.participant_id} style={{ borderBottom: '1px solid #f0ebe3' }}>
                          <td style={{ padding: '12px 14px', color: '#005B5C', fontWeight: '900', fontSize: '18px' }}>{idx + 1}</td>
                          <td style={{ padding: '12px 14px', color: '#555', fontWeight: '700' }}>{p.lot_number || '—'}</td>
                          <td style={{ padding: '12px 14px', color: '#888' }}>#{p.bib_no || '—'}</td>
                          <td style={{ padding: '12px 14px', color: '#1a1a1a', fontWeight: '600' }}>{p.first_name} {p.last_name}</td>
                          <td style={{ padding: '12px 14px', color: '#888', fontSize: '12px' }}>{p.country || '—'}</td>
                        </tr>
                      ))}
                      {soParticipants.length === 0 && (
                        <tr><td colSpan="5" style={{ padding: '32px', textAlign: 'center', color: '#aaa', fontSize: '13px' }}>No draw yet. Run the draw in the Draw tab first.</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {tab === 'Protocol' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div style={{ color: '#005B5C', fontSize: '10px', letterSpacing: '3px' }}>COMPETITION PROTOCOL</div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <a href={`https://api.events.worldstrongman.org/competitions/${competitionId}/protocol`} target="_blank" style={{ padding: '8px 18px', background: 'transparent', border: '1px solid #005B5C', color: '#005B5C', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🖨️ PRINT</a>
              <a href={`https://api.events.worldstrongman.org/competitions/${competitionId}/page`} target="_blank" style={{ padding: '8px 18px', background: 'transparent', border: '1px solid #333', color: '#888', borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none' }}>🌐 PUBLIC PAGE</a>
            </div>
          </div>
          {liveData && liveData.divisions.map(div => (
            <div key={div.division_id} style={{ marginBottom: '32px' }}>
              <div style={{ color: '#1a1a1a', fontSize: '13px', fontWeight: '700', letterSpacing: '3px', marginBottom: '12px', paddingBottom: '8px', borderBottom: '1px solid #005B5C' }}>{div.division_name}</div>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #e8e0d0' }}>
                      <th style={{ padding: '8px 10px', textAlign: 'left', color: '#888', fontSize: '9px' }}>PLACE</th>
                      <th style={{ padding: '8px 10px', textAlign: 'left', color: '#888', fontSize: '9px' }}>ATHLETE</th>
                      <th style={{ padding: '8px 10px', textAlign: 'left', color: '#888', fontSize: '9px' }}>COUNTRY</th>
                      {div.disciplines.map(d => <th key={d.id} style={{ padding: '8px 10px', textAlign: 'center', color: '#888', fontSize: '9px' }}>{d.name}</th>)}
                      <th style={{ padding: '8px 10px', textAlign: 'center', color: '#888', fontSize: '9px' }}>TOTAL</th>
                    </tr>
                  </thead>
                  <tbody>
                    {div.participants.map((p, idx) => {
                      const total = div.disciplines.reduce((sum, d) => sum + (parseFloat(d.results[p.participant_id]) || 0), 0);
                      return (
                        <tr key={p.participant_id} style={{ borderBottom: '1px solid #f0ebe3' }}>
                          <td style={{ padding: '10px', color: '#005B5C', fontWeight: '900', fontSize: '18px' }}>{idx+1}</td>
                          <td style={{ padding: '10px', color: '#1a1a1a', fontWeight: '600' }}>{p.first_name} {p.last_name}</td>
                          <td style={{ padding: '10px', color: '#888', fontSize: '12px' }}>{p.country||'-'}</td>
                          {div.disciplines.map(d => <td key={d.id} style={{ padding: '10px', textAlign: 'center', color: '#888' }}>{d.results[p.participant_id]||'-'}</td>)}
                          <td style={{ padding: '10px', textAlign: 'center', color: '#005B5C', fontWeight: '700' }}>{total ? total.toFixed(1) : '-'}</td>
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
          <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '20px', marginBottom: '24px' }}>
            <div style={{ color: '#005B5C', fontSize: '10px', letterSpacing: '3px', marginBottom: '16px' }}>INVITE JUDGE BY EMAIL</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '12px', alignItems: 'end' }}>
              <div>
                <label style={labelStyle}>Email</label>
                <input style={inputStyle} type="email" placeholder="judge@example.com" value={inviteForm.email} onChange={e => setInviteForm(f => ({ ...f, email: e.target.value }))} />
              </div>
              <div>
                <label style={labelStyle}>Name</label>
                <input style={inputStyle} placeholder="John Smith" value={inviteForm.name} onChange={e => setInviteForm(f => ({ ...f, name: e.target.value }))} />
              </div>
              <button onClick={sendInvite} disabled={sendingInvite} style={{ padding: '11px 20px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: sendingInvite ? 'not-allowed' : 'pointer', opacity: sendingInvite ? 0.7 : 1, whiteSpace: 'nowrap' }}>
                {sendingInvite ? 'GENERATING...' : 'GENERATE INVITE LINK →'}
              </button>
            </div>
            {lastInviteLink && (
              <div style={{ marginTop: '16px', background: '#f0faf0', border: '1px solid #c8e6c9', borderRadius: '4px', padding: '16px' }}>
                <div style={{ color: '#2e7d32', fontSize: '13px', fontWeight: '600', marginBottom: '10px' }}>✅ Link created! Share with judge:</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                  <div style={{ flex: 1, background: '#fff', border: '1px solid #c8e6c9', borderRadius: '3px', padding: '8px 12px', fontSize: '12px', color: '#333', wordBreak: 'break-all' }}>{lastInviteLink}</div>
                  <button onClick={() => navigator.clipboard.writeText(lastInviteLink)} style={{ padding: '8px 14px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer', whiteSpace: 'nowrap' }}>Copy</button>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px' }}>
                  <span style={{ color: '#888' }}>Send via:</span>
                  <a href={`mailto:?subject=Judge+Invitation&body=${encodeURIComponent(lastInviteLink)}`} style={{ color: '#005B5C', fontWeight: '600', textDecoration: 'none' }}>Email</a>
                  <span style={{ color: '#ddd' }}>·</span>
                  <a href={`https://wa.me/?text=${encodeURIComponent('Join as judge: ' + lastInviteLink)}`} target="_blank" rel="noopener noreferrer" style={{ color: '#25d366', fontWeight: '600', textDecoration: 'none' }}>WhatsApp</a>
                  <span style={{ color: '#ddd' }}>·</span>
                  <a href={`https://t.me/share/url?url=${encodeURIComponent(lastInviteLink)}&text=${encodeURIComponent('Join as judge')}`} target="_blank" rel="noopener noreferrer" style={{ color: '#229ED9', fontWeight: '600', textDecoration: 'none' }}>Telegram</a>
                </div>
              </div>
            )}
          </div>
          <div style={{ color: '#005B5C', fontSize: '10px', letterSpacing: '3px', marginBottom: '12px' }}>INVITATIONS ({judges.length})</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {judges.map(j => (
              <div key={j.id} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ color: '#1a1a1a', fontWeight: '600', marginBottom: '2px' }}>{j.name}</div>
                  <div style={{ color: '#888', fontSize: '12px' }}>{j.email}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ background: j.status === 'used' ? 'rgba(0,91,92,0.08)' : 'rgba(255,193,7,0.12)', color: j.status === 'used' ? '#005B5C' : '#b8860b', fontSize: '10px', fontWeight: '700', padding: '3px 8px', borderRadius: '2px', letterSpacing: '1px' }}>{(j.status || 'pending').toUpperCase()}</div>
                  {j.status !== 'used' && j.token && (
                    <button onClick={() => { navigator.clipboard.writeText(`https://events.worldstrongman.org/judge/${j.token}`); }} style={{ background: 'transparent', border: '1px solid #e8e0d0', color: '#555', padding: '4px 10px', borderRadius: '3px', cursor: 'pointer', fontSize: '11px' }}>Copy link</button>
                  )}
                </div>
              </div>
            ))}
            {judges.length === 0 && <p style={{ color: '#888' }}>No invitations sent yet.</p>}
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
            <div style={{ color: '#005B5C', fontSize: '10px', letterSpacing: '3px' }}>APPLICATIONS ({registrations.length})</div>
            <button onClick={async () => { const res = await axios.get(`${API}/competitions/${competitionId}/registrations`, authCfg()); setRegistrations(res.data); }} style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #333', color: '#666', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>🔄 REFRESH</button>
          </div>
          {registrations.length === 0 && <p style={{ color: '#888' }}>No applications yet.</p>}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {registrations.map(r => (
              <div key={r.id} style={{ background: '#fff', border: `1px solid ${r.status === 'PAID' ? '#c8e6c9' : r.status === 'PENDING' ? '#e8e0d0' : r.status === 'ACCEPTED' ? '#c8e6c9' : '#ffcdd2'}`, borderRadius: '4px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
                    <span style={{ color: r.status === 'PAID' ? '#2e7d32' : r.status === 'PENDING' ? '#005B5C' : r.status === 'ACCEPTED' ? '#2e7d32' : '#c62828', fontSize: '10px', fontWeight: '700', letterSpacing: '2px' }}>{r.status}</span>
                    <span style={{ color: '#1a1a1a', fontWeight: '600' }}>{r.athlete_name}</span>
                    <span style={{ color: '#888', fontSize: '12px' }}>{r.country}</span>
                    <span style={{ color: '#005B5C', fontSize: '12px' }}>{r.division_key}</span>
                  </div>
                  <div style={{ color: '#888', fontSize: '11px' }}>{r.athlete_email} · {r.payment_method === 'crypto' ? '₿ USDT' : '💳 Card'} · <span style={{color: r.status === 'PAID' ? '#2e7d32' : '#005B5C'}}>€{r.amount_eur}</span>{r.coupon_code && <span style={{color:'#0097a7', marginLeft:'8px'}}>🏷️ {r.coupon_code}</span>}</div>
                  <div style={{ color: '#aaa', fontSize: '10px', marginTop: '2px' }}>{r.created_at ? new Date(r.created_at).toLocaleString() : ''}</div>
                </div>
                {r.status === 'PENDING' && (
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={async () => { await axios.patch(`${API}/competitions/${competitionId}/registrations/${r.id}`, { status: 'ACCEPTED' }, authCfg()); const res = await axios.get(`${API}/competitions/${competitionId}/registrations`, authCfg()); setRegistrations(res.data); }} style={{ padding: '8px 16px', background: '#2a4a2a', border: '1px solid #4caf50', color: '#4caf50', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>✓ ACCEPT</button>
                    <button onClick={async () => { const reason = prompt('Reject reason (optional):'); await axios.patch(`${API}/competitions/${competitionId}/registrations/${r.id}`, { status: 'REJECTED', reject_reason: reason || '' }, authCfg()); const res = await axios.get(`${API}/competitions/${competitionId}/registrations`, authCfg()); setRegistrations(res.data); }} style={{ padding: '8px 16px', background: '#4a2a2a', border: '1px solid #f44336', color: '#f44336', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>✕ REJECT</button>
                  </div>
                )}
                {r.status === 'PAID' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', minWidth: '160px' }}>
                    <select
                      id={`div-select-${r.id}`}
                      style={{ padding: '6px 10px', background: '#fff', border: '1px solid #e8e0d0', color: '#1a1a1a', borderRadius: '3px', fontSize: '11px' }}
                      defaultValue=""
                    >
                      <option value="">Select division...</option>
                      {divisions.map(d => <option key={d.id} value={d.id}>{d.name || d.division_key}</option>)}
                    </select>
                    <button onClick={async () => {
                      const divId = document.getElementById(`div-select-${r.id}`).value;
                      if (!divId) { alert('Select a division first'); return; }
                      try {
                        await api.post('/participants/', { events_division_id: divId, competition_id: competitionId, athlete_id: r.athlete_id });
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
      <div className="wsm-banner-wrap" style={{ marginTop: '32px', background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '20px', marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {competition.banner_url
          ? <img src={competition.banner_url?.startsWith('http') ? competition.banner_url : `https://api.events.worldstrongman.org${competition.banner_url}`} style={{ width: '100%', maxWidth: '300px', height: '120px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #e8e0d0' }} />
          : <div style={{ width: '100%', maxWidth: '300px', height: '120px', background: '#f7f4ef', border: '1px dashed #e8e0d0', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#aaa', fontSize: '12px' }}>No banner</div>
        }
        <div style={{ flex: '1', minWidth: '200px' }}>
          <div style={{ color: '#888', fontSize: '11px', letterSpacing: '2px', marginBottom: '8px' }}>COMPETITION BANNER</div>
          <label style={{ padding: '10px 20px', background: '#005B5C', color: '#fff', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', display: 'inline-block' }}>
            🖼️ {bannerUploading ? 'UPLOADING...' : 'UPLOAD BANNER'}
            <input type="file" accept=".jpg,.jpeg,.png,.webp" style={{ display: 'none' }} onChange={e => e.target.files[0] && uploadBanner(e.target.files[0])} />
          </label>
          <div style={{ color: '#aaa', fontSize: '11px', marginTop: '6px' }}>Recommended: 1500×640px · JPG/PNG · max 2MB</div>
        </div>
      </div>

      <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '20px', marginBottom: '20px' }}>
        <div style={{ color: '#005B5C', fontSize: '10px', letterSpacing: '3px', marginBottom: '16px' }}>SPONSORS ({sponsors.length}/6)</div>
        {sponsors.map(s => (
          <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 0', borderBottom: '1px solid #f0ebe3' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              {s.logo_url ? <img src={s.logo_url?.startsWith("http") ? s.logo_url : `https://api.events.worldstrongman.org${s.logo_url}`} style={{ width: '80px', height: '50px', objectFit: 'contain', background: '#f7f4ef', borderRadius: '4px' }} /> : <div style={{ width: '80px', height: '50px', background: '#f7f4ef', border: '1px dashed #e8e0d0', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#aaa' }}>🎽</div>}
              <label style={{ padding: '3px 8px', border: '1px solid #005B5C', color: '#005B5C', fontSize: '9px', fontWeight: '700', cursor: 'pointer', borderRadius: '2px' }}>
                📷 LOGO
                <input type="file" accept=".jpg,.jpeg,.png,.webp" style={{ display: 'none' }} onChange={async e => { if (!e.target.files[0]) return; const fd = new FormData(); fd.append('file', e.target.files[0]); const res = await axios.post(`${API}/competitions/${competitionId}/sponsors/${s.id}/logo`, fd, authCfg()); setSponsors(sponsors.map(sp => sp.id === s.id ? {...sp, logo_url: res.data.logo_url} : sp)); }} />
              </label>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span style={{ color: s.tier === 'PAID' ? '#005B5C' : '#888', fontSize: '10px', fontWeight: '700', background: s.tier === 'PAID' ? 'rgba(0,91,92,0.08)' : '#f0ebe3', padding: '2px 6px', borderRadius: '2px' }}>{s.tier}</span>
                <span style={{ color: '#1a1a1a', fontSize: '14px', fontWeight: '600' }}>{s.name}</span>
              </div>
              {s.website_url && <a href={s.website_url} target="_blank" style={{ color: '#555', fontSize: '11px', textDecoration: 'none' }}>{s.website_url}</a>}
            </div>
            <button onClick={() => deleteSponsor(s.id)} style={{ background: 'transparent', border: '1px solid #e8e0d0', color: '#888', padding: '3px 8px', borderRadius: '3px', cursor: 'pointer', fontSize: '11px' }}>✕</button>
          </div>
        ))}
        {sponsors.length < 6 && (
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end', marginTop: '16px', flexWrap: 'wrap' }}>
            <div style={{ flex: 2 }}><label style={labelStyle}>NAME</label><input value={newSponsor.name} onChange={e => setNewSponsor({...newSponsor, name: e.target.value})} placeholder="Sponsor name" style={inputStyle} /></div>
            <div style={{ flex: 2 }}><label style={labelStyle}>WEBSITE</label><input value={newSponsor.website_url} onChange={e => setNewSponsor({...newSponsor, website_url: e.target.value})} placeholder="https://..." style={inputStyle} /></div>
            <div style={{ flex: 1 }}><label style={labelStyle}>TYPE</label><select value={newSponsor.tier} onChange={e => setNewSponsor({...newSponsor, tier: e.target.value})} style={inputStyle}><option value="FREE">FREE</option><option value="PAID">PAID</option></select></div>
            <button onClick={addSponsor} style={{ padding: '10px 16px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>+ ADD</button>
          </div>
        )}
      </div>

      <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '24px', marginBottom: '24px' }}>
        <div style={{ color: '#005B5C', fontSize: '10px', letterSpacing: '3px', marginBottom: '16px' }}>COMPETITION INFO</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          {[['name','NAME'],['city','CITY'],['country','COUNTRY'],['organizer_email','ORGANIZER EMAIL'],['date_start','DATE START'],['date_end','DATE END']].map(([field, label]) => (
            <div key={field}><label style={labelStyle}>{label}</label><input style={inputStyle} value={editForm[field]||''} onChange={e => setEditForm({...editForm, [field]: e.target.value})} /></div>
          ))}
        </div>
        
        {/* ENTRY FEE SECTION */}
        <div style={{ marginTop: '24px', padding: '16px', background: '#f0fbf0', border: '1px solid #c8e6c9', borderRadius: '6px' }}>
          <div style={{ color: '#2e7d32', fontSize: '10px', letterSpacing: '3px', marginBottom: '14px' }}>💰 ENTRY FEE SETTINGS</div>
          
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
              <div style={{ gridColumn: '1/-1', display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', background: '#fff5f5', borderRadius: '4px', border: '1px solid #ffcdd2' }}>
                <input
                  type="checkbox"
                  id="non_refundable"
                  checked={editForm.entry_fee_non_refundable !== false}
                  onChange={e => setEditForm({...editForm, entry_fee_non_refundable: e.target.checked})}
                  style={{ width: '14px', height: '14px' }}
                />
                <label htmlFor="non_refundable" style={{ color: '#c62828', fontSize: '11px', letterSpacing: '1px', cursor: 'pointer' }}>
                  ⚠️ Entry fee is NON-REFUNDABLE — athlete confirms at registration
                </label>
              </div>
              <div style={{ gridColumn: '1/-1', padding: '10px', background: '#f0fbf0', borderRadius: '4px', fontSize: '11px', color: '#666' }}>
                💰 WSM Commission: <span style={{color:'#005B5C'}}>15%</span> &nbsp;·&nbsp;
                Organizer payout: <span style={{color:'#2e7d32'}}>85%</span> &nbsp;·&nbsp;
                Payout after registration deadline
              </div>
            </div>
          )}
        </div>

        
<button onClick={saveCompetition} disabled={saving} style={{ marginTop: '16px', padding: '10px 24px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', letterSpacing: '1px' }}>
          {saving ? 'SAVING...' : 'SAVE CHANGES →'}
        </button>
      </div>
    </Layout>
  );
}
