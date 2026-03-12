import { useState, useEffect } from 'react';
import { useAuth } from '../../AuthContext';
import Layout from '../../components/Layout';
import axios from 'axios';

const gold = '#c9a84c';
const API = 'https://ranking.worldstrongman.org';

export default function TeamProfile() {
  const { user } = useAuth();
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');
  const [form, setForm] = useState({});
  const [sponsors, setSponsors] = useState([]);
  const [newSponsor, setNewSponsor] = useState({ name: '', website_url: '', tier: 'STANDARD' });
  const [teamId, setTeamId] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    axios.get(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => {
        const tid = res.data.team_id;
        if (!tid) { setLoading(false); return; }
        setTeamId(tid);
        return axios.get(`${API}/teams/${tid}/room`);
      })
      .then(res => {
        if (!res) return;
        const t = res.data.team || res.data;
        setTeam(t);
        setForm({ name: t.name||'', country: t.country||'', email: t.email||'' });
      })
      .finally(() => setLoading(false));
    if (tid) {
      axios.get(`${API}/teams/${tid}/sponsors`)
        .then(res => setSponsors(res.data))
        .catch(() => {});
    }
  }, [user]);

  const save = async () => {
    setSaving(true); setMsg(''); setError('');
    try {
      const token = localStorage.getItem('token');
      await axios.patch(`${API}/teams/${teamId}`, form, { headers: { Authorization: `Bearer ${token}` } });
      setMsg('Team info saved!');
    } catch(e) { setError(e.response?.data?.detail || 'Save failed'); }
    finally { setSaving(false); }
  };

  const uploadFile = async (file, type) => {
    const token = localStorage.getItem('token');
    const fd = new FormData(); fd.append('file', file);
    const endpoint = type === 'logo' ? 'logo' : 'team-photo';
    await axios.post(`${API}/teams/${teamId}/${endpoint}`, fd, { headers: { Authorization: `Bearer ${token}` } });
    window.location.reload();
  };

  const addSponsor = async () => {
    if (!newSponsor.name.trim()) return;
    const token = localStorage.getItem('token');
    const res = await axios.post(`${API}/teams/${teamId}/sponsors`,
      newSponsor, { headers: { Authorization: `Bearer ${token}` } }
    );
    setSponsors([...sponsors, res.data]);
    setNewSponsor({ name: '', website_url: '', tier: 'STANDARD' });
  };

  const deleteSponsor = async (sid) => {
    const token = localStorage.getItem('token');
    await axios.delete(`${API}/teams/${teamId}/sponsors/${sid}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setSponsors(sponsors.filter(s => s.id !== sid));
  };

  if (loading) return <Layout><p style={{color:'#555'}}>Loading...</p></Layout>;
  if (!teamId) return <Layout><p style={{color:'#ff5252'}}>No team profile linked.</p></Layout>;

  return (
    <Layout>
      <div style={{marginBottom:'32px'}}>
        <div style={{color:gold,fontSize:'11px',letterSpacing:'3px',marginBottom:'8px'}}>TEAM CABINET</div>
        <h1 style={{color:'#fff',fontSize:'22px',fontWeight:'700',margin:'0 0 4px'}}>My Team</h1>
        <p style={{color:'#555',fontSize:'13px',margin:0}}>Manage your team profile</p>
      </div>

      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px',display:'flex',alignItems:'center',gap:'24px',flexWrap:'wrap'}}>
        <div>
          {team?.logo_url ? <img src={`${API}${team.logo_url}`} style={{width:'80px',height:'80px',objectFit:'cover',border:`2px solid ${gold}`,borderRadius:'4px'}} />
            : <div style={{width:'80px',height:'80px',background:'#1a1a1a',border:'1px solid #2a2a2a',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'28px',borderRadius:'4px'}}>👥</div>}
          <label style={{display:'block',marginTop:'8px',padding:'5px 10px',border:`1px solid ${gold}`,color:gold,fontSize:'10px',fontWeight:'700',cursor:'pointer',borderRadius:'3px',textAlign:'center'}}>
            📷 LOGO<input type="file" accept=".jpg,.jpeg,.png,.webp" style={{display:'none'}} onChange={e=>e.target.files[0]&&uploadFile(e.target.files[0],'logo')} />
          </label>
        </div>
        <div>
          {team?.team_photo_url ? <img src={`${API}${team.team_photo_url}`} style={{width:'120px',height:'80px',objectFit:'cover',border:'1px solid #2a2a2a',borderRadius:'4px'}} />
            : <div style={{width:'120px',height:'80px',background:'#1a1a1a',border:'1px solid #2a2a2a',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'12px',color:'#444',borderRadius:'4px'}}>TEAM PHOTO</div>}
          <label style={{display:'block',marginTop:'8px',padding:'5px 10px',border:'1px solid #2a2a2a',color:'#666',fontSize:'10px',fontWeight:'700',cursor:'pointer',borderRadius:'3px',textAlign:'center'}}>
            📷 TEAM PHOTO<input type="file" accept=".jpg,.jpeg,.png,.webp" style={{display:'none'}} onChange={e=>e.target.files[0]&&uploadFile(e.target.files[0],'team-photo')} />
          </label>
        </div>
        <div>
          <div style={{color:'#fff',fontWeight:'700',fontSize:'18px',marginBottom:'4px'}}>{team?.name}</div>
          <div style={{color:'#555',fontSize:'12px'}}>{team?.country || '—'}</div>
          <div style={{marginTop:'8px',padding:'3px 8px',border:'1px solid #555',color:'#555',fontSize:'10px',letterSpacing:'1px',display:'inline-block'}}>{team?.status?.toUpperCase() || 'PENDING'}</div>
        </div>
      </div>

      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px'}}>
        <div style={{color:gold,fontSize:'10px',letterSpacing:'3px',marginBottom:'20px',paddingBottom:'8px',borderBottom:'1px solid #1e1e1e'}}>TEAM INFO</div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'14px'}}>
          {[{id:'name',label:'Team Name'},{id:'country',label:'Country'},{id:'email',label:'Contact Email'}].map(f => (
            <div key={f.id} style={{display:'flex',flexDirection:'column',gap:'6px',gridColumn: f.id==='email'?'1/-1':'auto'}}>
              <label style={{color:'#888',fontSize:'10px',fontWeight:'700',letterSpacing:'1px',textTransform:'uppercase'}}>{f.label}</label>
              <input type="text" value={form[f.id]||''} onChange={e=>setForm({...form,[f.id]:e.target.value})}
                style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'14px',outline:'none',width:'100%',boxSizing:'border-box'}} />
            </div>
          ))}
        </div>
      </div>

      {team?.members?.length > 0 && (
        <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px'}}>
          <div style={{color:gold,fontSize:'10px',letterSpacing:'3px',marginBottom:'16px',paddingBottom:'8px',borderBottom:'1px solid #1e1e1e'}}>SQUAD</div>
          {team.members.map(m => (
            <div key={m.id} style={{display:'flex',alignItems:'center',gap:'12px',padding:'10px 0',borderBottom:'1px solid #1a1a1a'}}>
              {m.athlete?.photo_url ? <img src={`${API}${m.athlete.photo_url}`} style={{width:'40px',height:'40px',borderRadius:'50%',objectFit:'cover'}} />
                : <div style={{width:'40px',height:'40px',borderRadius:'50%',background:'#1a1a1a',display:'flex',alignItems:'center',justifyContent:'center'}}>💪</div>}
              <div>
                <div style={{color:'#fff',fontWeight:'600',fontSize:'14px'}}>{m.athlete?.first_name} {m.athlete?.last_name}</div>
                <div style={{color:'#555',fontSize:'11px'}}>{m.role} · {m.athlete?.country}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px'}}>
        <div style={{color:gold,fontSize:'10px',letterSpacing:'3px',marginBottom:'16px',paddingBottom:'8px',borderBottom:'1px solid #1e1e1e'}}>SPONSORS</div>
        
        {/* General sponsor - большой */}
        {sponsors.filter(s=>s.tier==='GENERAL').map(s => (
          <div key={s.id} style={{display:'flex',alignItems:'center',gap:'16px',padding:'16px',background:'rgba(201,168,76,0.05)',border:'1px solid rgba(201,168,76,0.2)',borderRadius:'4px',marginBottom:'12px'}}>
            {s.logo_url ? <img src={`${API}${s.logo_url}`} style={{width:'80px',height:'60px',objectFit:'contain',background:'#1a1a1a',borderRadius:'3px'}} />
              : <div style={{width:'80px',height:'60px',background:'#1a1a1a',borderRadius:'3px',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'24px'}}>🏆</div>}
            <div style={{flex:1}}>
              <div style={{color:gold,fontSize:'10px',letterSpacing:'2px',marginBottom:'4px'}}>GENERAL SPONSOR</div>
              <div style={{color:'#fff',fontWeight:'700',fontSize:'16px'}}>{s.name}</div>
              {s.website_url && <a href={s.website_url} target="_blank" style={{color:'#555',fontSize:'11px'}}>{s.website_url}</a>}
            </div>
            <button onClick={()=>deleteSponsor(s.id)} style={{background:'transparent',border:'1px solid #333',color:'#666',padding:'4px 10px',borderRadius:'3px',cursor:'pointer',fontSize:'11px'}}>✕</button>
          </div>
        ))}

        {/* Standard sponsors - поменьше */}
        {sponsors.filter(s=>s.tier==='STANDARD').map(s => (
          <div key={s.id} style={{display:'flex',alignItems:'center',gap:'12px',padding:'10px',background:'#0a0a0a',border:'1px solid #1e1e1e',borderRadius:'4px',marginBottom:'8px'}}>
            {s.logo_url ? <img src={`${API}${s.logo_url}`} style={{width:'48px',height:'36px',objectFit:'contain',background:'#1a1a1a',borderRadius:'3px'}} />
              : <div style={{width:'48px',height:'36px',background:'#1a1a1a',borderRadius:'3px',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'16px'}}>🎽</div>}
            <div style={{flex:1}}>
              <div style={{color:'#888',fontSize:'10px',letterSpacing:'1px',marginBottom:'2px'}}>STANDARD SPONSOR</div>
              <div style={{color:'#fff',fontWeight:'600',fontSize:'13px'}}>{s.name}</div>
            </div>
            <button onClick={()=>deleteSponsor(s.id)} style={{background:'transparent',border:'1px solid #333',color:'#666',padding:'4px 10px',borderRadius:'3px',cursor:'pointer',fontSize:'11px'}}>✕</button>
          </div>
        ))}

        {/* Добавить нового спонсора */}
        {(sponsors.filter(s=>s.tier==='GENERAL').length < 1 || sponsors.filter(s=>s.tier==='STANDARD').length < 2) && (
          <div style={{marginTop:'16px',display:'grid',gridTemplateColumns:'1fr 1fr 120px auto',gap:'10px',alignItems:'end'}}>
            <div>
              <label style={{color:'#888',fontSize:'10px',fontWeight:'700',display:'block',marginBottom:'6px'}}>SPONSOR NAME</label>
              <input value={newSponsor.name} onChange={e=>setNewSponsor({...newSponsor,name:e.target.value})} placeholder="Name"
                style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'13px',outline:'none',width:'100%',boxSizing:'border-box'}} />
            </div>
            <div>
              <label style={{color:'#888',fontSize:'10px',fontWeight:'700',display:'block',marginBottom:'6px'}}>WEBSITE</label>
              <input value={newSponsor.website_url} onChange={e=>setNewSponsor({...newSponsor,website_url:e.target.value})} placeholder="https://..."
                style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'13px',outline:'none',width:'100%',boxSizing:'border-box'}} />
            </div>
            <div>
              <label style={{color:'#888',fontSize:'10px',fontWeight:'700',display:'block',marginBottom:'6px'}}>TYPE</label>
              <select value={newSponsor.tier} onChange={e=>setNewSponsor({...newSponsor,tier:e.target.value})}
                style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'13px',outline:'none',width:'100%'}}>
                {sponsors.filter(s=>s.tier==='GENERAL').length < 1 && <option value="GENERAL">General</option>}
                {sponsors.filter(s=>s.tier==='STANDARD').length < 2 && <option value="STANDARD">Standard</option>}
              </select>
            </div>
            <button onClick={addSponsor} style={{padding:'10px 16px',background:gold,color:'#000',border:'none',borderRadius:'3px',fontSize:'12px',fontWeight:'700',cursor:'pointer'}}>+ ADD</button>
          </div>
        )}
      </div>

      {msg && <div style={{background:'rgba(76,175,80,0.1)',border:'1px solid #4caf50',color:'#4caf50',padding:'12px 16px',borderRadius:'3px',marginBottom:'16px'}}>✓ {msg}</div>}
      {error && <div style={{background:'rgba(255,82,82,0.1)',border:'1px solid #ff5252',color:'#ff5252',padding:'12px 16px',borderRadius:'3px',marginBottom:'16px'}}>✗ {error}</div>}

      <button onClick={save} disabled={saving} style={{width:'100%',padding:'14px',background:gold,color:'#000',border:'none',borderRadius:'3px',fontSize:'13px',fontWeight:'900',letterSpacing:'2px',cursor:'pointer',textTransform:'uppercase'}}>
        {saving ? 'SAVING...' : 'SAVE TEAM →'}
      </button>
    </Layout>
  );
}