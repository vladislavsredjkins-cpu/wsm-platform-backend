import { useEffect, useState } from 'react';
import api from '../api';

const gold = '#c9a84c';
const inputStyle = { width: '100%', padding: '10px 14px', background: '#0a0a0a', border: '1px solid #2a2a2a', color: '#fff', borderRadius: '3px', fontSize: '13px', outline: 'none' };
const labelStyle = { display: 'block', color: '#555', fontSize: '10px', letterSpacing: '2px', marginBottom: '6px' };
const sectionStyle = { background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '24px', marginBottom: '20px' };
const sectionTitle = { color: gold, fontSize: '10px', letterSpacing: '3px', marginBottom: '16px' };

export default function MCTab({ competitionId, competition }) {
  const [mcSection, setMcSection] = useState('info');
  const [saving, setSaving] = useState(false);
  const [mcInfo, setMcInfo] = useState({ description: '', organizer_mc_text: '' });
  const [program, setProgram] = useState([]);
  const [guests, setGuests] = useState([]);
  const [sponsors, setSponsors] = useState([]);
  const [sponsorTexts, setSponsorTexts] = useState({});
  const [newProgram, setNewProgram] = useState({ time_slot: '', type: 'CEREMONY', title: '', description: '', person_name: '', person_role: '' });
  const [newGuest, setNewGuest] = useState({ name: '', title: '', country: '', bio: '' });

  useEffect(() => {
    if (competition) {
      setMcInfo({ description: competition.description || '', organizer_mc_text: competition.organizer_mc_text || '' });
    }
    api.get(`/competitions/${competitionId}/mc-data`).then(r => {
      setProgram(r.data.program || []);
      setGuests(r.data.guests || []);
      setSponsors(r.data.sponsors || []);
      const texts = {};
      (r.data.sponsors || []).forEach(s => { texts[s.id] = s.mc_text || ''; });
      setSponsorTexts(texts);
    }).catch(() => {});
  }, [competitionId, competition]);

  const saveInfo = async () => {
    setSaving(true);
    try {
      await api.patch(`/competitions/${competitionId}`, mcInfo);
      alert('Saved!');
    } catch(e) { alert('Error saving'); }
    finally { setSaving(false); }
  };

  const addProgram = async () => {
    if (!newProgram.title) return;
    try {
      const res = await api.post(`/competitions/${competitionId}/program`, newProgram);
      setProgram([...program, res.data]);
      setNewProgram({ time_slot: '', type: 'CEREMONY', title: '', description: '', person_name: '', person_role: '' });
    } catch(e) { alert('Error'); }
  };

  const deleteProgram = async (id) => {
    try {
      await api.delete(`/competitions/${competitionId}/program/${id}`);
      setProgram(program.filter(p => p.id !== id));
    } catch(e) { alert('Error'); }
  };

  const addGuest = async () => {
    if (!newGuest.name) return;
    try {
      const res = await api.post(`/competitions/${competitionId}/guests`, newGuest);
      setGuests([...guests, res.data]);
      setNewGuest({ name: '', title: '', country: '', bio: '' });
    } catch(e) { alert('Error'); }
  };

  const deleteGuest = async (id) => {
    try {
      await api.delete(`/competitions/${competitionId}/guests/${id}`);
      setGuests(guests.filter(g => g.id !== id));
    } catch(e) { alert('Error'); }
  };

  const [savedSponsor, setSavedSponsor] = useState(null);
  const saveSponsorMcText = async (sponsorId, mc_text) => {
    try {
      await api.patch(`/competitions/${competitionId}/sponsors/${sponsorId}`, { mc_text });
      setSavedSponsor(sponsorId);
      setTimeout(() => setSavedSponsor(null), 2000);
    } catch(e) { alert('Error'); }
  };

  const subTabs = ['INFO', 'PROGRAM', 'GUESTS', 'SPONSORS'];

  return (
    <div style={{ padding: '24px 0' }}>
      {/* Sub-tabs */}
      <div style={{ display: 'flex', gap: '0', borderBottom: '1px solid #1e1e1e', marginBottom: '24px' }}>
        {subTabs.map(t => (
          <button type="button" key={t} onClick={() => setMcSection(t.toLowerCase())}
            style={{ background: 'none', border: 'none', color: mcSection === t.toLowerCase() ? gold : '#555', padding: '10px 20px', cursor: 'pointer', fontSize: '11px', fontWeight: mcSection === t.toLowerCase() ? '700' : '400', borderBottom: mcSection === t.toLowerCase() ? `2px solid ${gold}` : '2px solid transparent', letterSpacing: '2px' }}>
            {t}
          </button>
        ))}
        <a href={`https://ranking.worldstrongman.org/competitions/${competitionId}/mc`} target="_blank"
          style={{ marginLeft: 'auto', padding: '8px 16px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '11px', fontWeight: '700', textDecoration: 'none', alignSelf: 'center', letterSpacing: '1px' }}>
          👁 PREVIEW MC SCREEN →
        </a>
        <button type="button" onClick={() => { navigator.clipboard.writeText(`https://ranking.worldstrongman.org/competitions/${competitionId}/mc`); alert('Link copied!'); }}
          style={{ marginLeft: '8px', padding: '8px 16px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer', letterSpacing: '1px' }}>📋 COPY LINK</button>
      </div>

      {/* INFO */}
      {mcSection === 'info' && (
        <div>
          <div style={sectionStyle}>
            <div style={sectionTitle}>TOURNAMENT INFO FOR MC</div>
            <label style={labelStyle}>DESCRIPTION / ABOUT THE COMPETITION</label>
            <textarea value={mcInfo.description} onChange={e => setMcInfo({...mcInfo, description: e.target.value})}
              placeholder="What MC should say about this competition..."
              style={{ ...inputStyle, minHeight: '120px', resize: 'vertical' }} />
          </div>
          <div style={sectionStyle}>
            <div style={sectionTitle}>ORGANIZER INFO FOR MC</div>
            <label style={labelStyle}>WHAT MC SHOULD SAY ABOUT THE ORGANIZER</label>
            <textarea value={mcInfo.organizer_mc_text} onChange={e => setMcInfo({...mcInfo, organizer_mc_text: e.target.value})}
              placeholder="Organization name, history, mission..."
              style={{ ...inputStyle, minHeight: '120px', resize: 'vertical' }} />
          </div>
          <button onClick={saveInfo} disabled={saving}
            style={{ padding: '10px 28px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', letterSpacing: '1px' }}>
            {saving ? 'SAVING...' : 'SAVE →'}
          </button>
        </div>
      )}

      {/* PROGRAM */}
      {mcSection === 'program' && (
        <div>
          <div style={sectionStyle}>
            <div style={sectionTitle}>EVENT PROGRAM</div>
            {program.length === 0 && <p style={{ color: '#444', fontSize: '13px', marginBottom: '16px' }}>No program items yet.</p>}
            {program.map(p => (
              <div key={p.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', padding: '12px 0', borderBottom: '1px solid #0d0d0d' }}>
                <div style={{ minWidth: '70px', color: gold, fontSize: '13px', fontWeight: '700' }}>{p.time_slot}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13px', fontWeight: '700' }}>{p.title}</div>
                  {p.person_name && <div style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>{p.person_name}{p.person_role ? ` — ${p.person_role}` : ''}</div>}
                  {p.description && <div style={{ fontSize: '12px', color: '#555', marginTop: '4px' }}>{p.description}</div>}
                </div>
                <span style={{ fontSize: '10px', color: '#444', padding: '2px 8px', border: '1px solid #2a2a2a', borderRadius: '3px' }}>{p.type}</span>
                <button onClick={() => deleteProgram(p.id)} style={{ background: 'transparent', border: '1px solid #333', color: '#666', padding: '3px 8px', borderRadius: '3px', cursor: 'pointer', fontSize: '11px' }}>✕</button>
              </div>
            ))}
          </div>
          <div style={sectionStyle}>
            <div style={sectionTitle}>ADD PROGRAM ITEM</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr', gap: '12px', marginBottom: '12px' }}>
              <div><label style={labelStyle}>TIME</label><input value={newProgram.time_slot} onChange={e => setNewProgram({...newProgram, time_slot: e.target.value})} placeholder="09:00" style={inputStyle} /></div>
              <div><label style={labelStyle}>TYPE</label>
                <select value={newProgram.type} onChange={e => setNewProgram({...newProgram, type: e.target.value})} style={inputStyle}>
                  <option>CEREMONY</option><option>COMPETITION</option><option>BREAK</option><option>SPEECH</option><option>AWARDS</option><option>OTHER</option>
                </select>
              </div>
              <div><label style={labelStyle}>TITLE</label><input value={newProgram.title} onChange={e => setNewProgram({...newProgram, title: e.target.value})} placeholder="Opening ceremony" style={inputStyle} /></div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
              <div><label style={labelStyle}>PERSON NAME</label><input value={newProgram.person_name} onChange={e => setNewProgram({...newProgram, person_name: e.target.value})} placeholder="John Smith" style={inputStyle} /></div>
              <div><label style={labelStyle}>PERSON ROLE</label><input value={newProgram.person_role} onChange={e => setNewProgram({...newProgram, person_role: e.target.value})} placeholder="President WSM" style={inputStyle} /></div>
            </div>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>DESCRIPTION / MC TEXT</label><textarea value={newProgram.description} onChange={e => setNewProgram({...newProgram, description: e.target.value})} placeholder="What MC should announce..." style={{ ...inputStyle, minHeight: '80px', resize: 'vertical' }} /></div>
            <button onClick={addProgram} style={{ padding: '10px 24px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>+ ADD</button>
          </div>
        </div>
      )}

      {/* GUESTS */}
      {mcSection === 'guests' && (
        <div>
          <div style={sectionStyle}>
            <div style={sectionTitle}>VIP GUESTS</div>
            {guests.length === 0 && <p style={{ color: '#444', fontSize: '13px', marginBottom: '16px' }}>No guests yet.</p>}
            {guests.map(g => (
              <div key={g.id} style={{ display: 'flex', gap: '16px', alignItems: 'flex-start', padding: '12px 0', borderBottom: '1px solid #0d0d0d' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', fontWeight: '700' }}>{g.name}</div>
                  {g.title && <div style={{ fontSize: '12px', color: '#888', marginTop: '2px' }}>{g.title}{g.country ? ` · ${g.country}` : ''}</div>}
                  {g.bio && <div style={{ fontSize: '12px', color: '#555', marginTop: '4px' }}>{g.bio}</div>}
                </div>
                <button onClick={() => deleteGuest(g.id)} style={{ background: 'transparent', border: '1px solid #333', color: '#666', padding: '3px 8px', borderRadius: '3px', cursor: 'pointer', fontSize: '11px' }}>✕</button>
              </div>
            ))}
          </div>
          <div style={sectionStyle}>
            <div style={sectionTitle}>ADD GUEST</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
              <div><label style={labelStyle}>NAME</label><input value={newGuest.name} onChange={e => setNewGuest({...newGuest, name: e.target.value})} placeholder="Ivan Ivanov" style={inputStyle} /></div>
              <div><label style={labelStyle}>TITLE / POSITION</label><input value={newGuest.title} onChange={e => setNewGuest({...newGuest, title: e.target.value})} placeholder="President of Federation" style={inputStyle} /></div>
              <div><label style={labelStyle}>COUNTRY</label><input value={newGuest.country} onChange={e => setNewGuest({...newGuest, country: e.target.value})} placeholder="Latvia" style={inputStyle} /></div>
            </div>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>BIO / MC TEXT</label><textarea value={newGuest.bio} onChange={e => setNewGuest({...newGuest, bio: e.target.value})} placeholder="What MC should say about this guest..." style={{ ...inputStyle, minHeight: '80px', resize: 'vertical' }} /></div>
            <button onClick={addGuest} style={{ padding: '10px 24px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>+ ADD</button>
          </div>
        </div>
      )}

      {/* SPONSORS */}
      {mcSection === 'sponsors' && (
        <div style={sectionStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={sectionTitle}>SPONSOR MC TEXTS</div>
            <button type="button" onClick={() => api.get(`/competitions/${competitionId}/mc-data`).then(r => { setSponsors(r.data.sponsors || []); const t = {}; (r.data.sponsors||[]).forEach(s => {t[s.id]=s.mc_text||''}); setSponsorTexts(t); })} style={{ padding: '6px 14px', background: 'transparent', border: '1px solid #333', color: '#666', borderRadius: '3px', fontSize: '11px', cursor: 'pointer' }}>🔄 LOAD</button>
          </div>
          {sponsors.length === 0 && <p style={{ color: '#444', fontSize: '13px' }}>Click LOAD to fetch sponsors</p>}
          {sponsors.map(s => (
            <div key={s.id} style={{ padding: '16px 0', borderBottom: '1px solid #0d0d0d' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                {s.logo_url && <img src={'https://ranking.worldstrongman.org' + s.logo_url} style={{ height: '32px', objectFit: 'contain' }} />}
                <span style={{ fontWeight: '700', fontSize: '14px' }}>{s.name}</span>
                <span style={{ fontSize: '10px', color: '#444', padding: '2px 8px', border: '1px solid #2a2a2a', borderRadius: '3px' }}>{s.tier}</span>
              </div>
              <label style={labelStyle}>WHAT MC SHOULD SAY ABOUT THIS SPONSOR</label>
              <textarea value={sponsorTexts[s.id] || ''}
                onChange={e => setSponsorTexts({...sponsorTexts, [s.id]: e.target.value})}
                placeholder="Company description, product, why they support WSM..."
                style={{ ...inputStyle, minHeight: '80px', resize: 'vertical' }} />
              <button type="button" onClick={() => saveSponsorMcText(s.id, sponsorTexts[s.id] || '')}
                style={{ marginTop: '8px', padding: '8px 20px', background: savedSponsor === s.id ? '#1a3a1a' : gold, color: savedSponsor === s.id ? '#4caf50' : '#000', border: 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer' }}>{savedSponsor === s.id ? '✓ SAVED' : 'SAVE →'}</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
