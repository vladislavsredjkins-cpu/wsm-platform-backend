import { useState, useEffect } from 'react';
import { useAuth } from '../../AuthContext';
import Layout from '../../components/Layout';
import axios from 'axios';

const gold = '#c9a84c';
const API = 'https://ranking.worldstrongman.org';

export default function AthleteProfile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');
  const [form, setForm] = useState({});
  const [sponsors, setSponsors] = useState([]);
  const [newSponsor, setNewSponsor] = useState({ name: '', website_url: '' });

  useEffect(() => {
    if (!user?.athlete_id) return;
    axios.get(`${API}/athletes/${user.athlete_id}/profile`)
      .then(res => {
        const a = res.data.athlete || res.data;
        setProfile(a);
        setForm({
          first_name: a.first_name || '',
          last_name: a.last_name || '',
          country: a.country || '',
          gender: a.gender || '',
          date_of_birth: a.date_of_birth || '',
          bodyweight_kg: a.bodyweight_kg || '',
          phone: a.phone || '',
          instagram: a.instagram || '',
          bio: a.bio || '',
        });
      })
      .finally(() => setLoading(false));
    axios.get(`${API}/athletes/${user.athlete_id}/sponsors`)
      .then(res => setSponsors(res.data))
      .catch(() => {});
  }, [user]);

  const save = async () => {
    setSaving(true); setMsg(''); setError('');
    try {
      const token = localStorage.getItem('token');
      await axios.patch(`${API}/athletes/${user.athlete_id}`, form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMsg('✓ Profile saved!');
    } catch(e) {
      setError('✗ ' + (e.response?.data?.detail || 'Save failed'));
    } finally { setSaving(false); }
  };

  const uploadPhoto = async (file) => {
    const token = localStorage.getItem('token');
    const fd = new FormData(); fd.append('file', file);
    await axios.post(`${API}/athletes/${user.athlete_id}/photo`, fd, {
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
    });
    window.location.reload();
  };

  const addSponsor = async () => {
    if (!newSponsor.name.trim()) return;
    const token = localStorage.getItem('token');
    const res = await axios.post(`${API}/athletes/${user.athlete_id}/sponsors`,
      { ...newSponsor, tier: 'free' },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setSponsors([...sponsors, res.data]);
    setNewSponsor({ name: '', website_url: '' });
  };

  const deleteSponsor = async (sid) => {
    const token = localStorage.getItem('token');
    await axios.delete(`${API}/athletes/${user.athlete_id}/sponsors/${sid}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setSponsors(sponsors.filter(s => s.id !== sid));
  };

  if (loading) return <Layout><p style={{color:'#555'}}>Loading...</p></Layout>;
  if (!user?.athlete_id) return <Layout><p style={{color:'#ff5252'}}>No athlete profile linked to your account.</p></Layout>;

  return (
    <Layout>
      <div style={{marginBottom:'32px'}}>
        <div style={{color:gold,fontSize:'11px',letterSpacing:'3px',marginBottom:'8px'}}>ATHLETE CABINET</div>
        <h1 style={{color:'#fff',fontSize:'22px',fontWeight:'700',margin:'0 0 4px'}}>My Profile</h1>
        <p style={{color:'#555',fontSize:'13px',margin:0}}>Edit your public athlete profile</p>
      </div>

      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px',display:'flex',alignItems:'center',gap:'20px',flexWrap:'wrap'}}>
        {profile?.photo_url
          ? <img src={`${API}${profile.photo_url}`} style={{width:'80px',height:'80px',borderRadius:'50%',objectFit:'cover',border:`2px solid ${gold}`}} />
          : <div style={{width:'80px',height:'80px',borderRadius:'50%',background:'#1a1a1a',border:'1px solid #2a2a2a',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'28px'}}>💪</div>
        }
        <div>
          <div style={{color:'#fff',fontWeight:'700',fontSize:'16px',marginBottom:'4px'}}>{profile?.first_name} {profile?.last_name}</div>
          <div style={{color:'#555',fontSize:'12px',marginBottom:'12px'}}>{profile?.country || '—'}</div>
          <label style={{padding:'7px 16px',border:`1px solid ${gold}`,color:gold,fontSize:'11px',fontWeight:'700',letterSpacing:'2px',cursor:'pointer',borderRadius:'3px'}}>
            📷 CHANGE PHOTO
            <input type="file" accept=".jpg,.jpeg,.png,.webp" style={{display:'none'}} onChange={e => e.target.files[0] && uploadPhoto(e.target.files[0])} />
          </label>
        </div>
      </div>

      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px'}}>
        <div style={{color:gold,fontSize:'10px',letterSpacing:'3px',marginBottom:'20px',paddingBottom:'8px',borderBottom:'1px solid #1e1e1e'}}>PERSONAL INFO</div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'14px'}}>
          {[
            {id:'first_name',label:'First Name'},
            {id:'last_name',label:'Last Name'},
            {id:'country',label:'Country (e.g. LAT)'},
            {id:'gender',label:'Gender',type:'select',options:['male','female']},
            {id:'date_of_birth',label:'Date of Birth',type:'date'},
            {id:'bodyweight_kg',label:'Bodyweight (kg)',type:'number'},
            {id:'phone',label:'Phone'},
            {id:'instagram',label:'Instagram'},
          ].map(f => (
            <div key={f.id} style={{display:'flex',flexDirection:'column',gap:'6px'}}>
              <label style={{color:'#888',fontSize:'10px',fontWeight:'700',letterSpacing:'1px',textTransform:'uppercase'}}>{f.label}</label>
              {f.type === 'select'
                ? <select value={form[f.id]||''} onChange={e=>setForm({...form,[f.id]:e.target.value})}
                    style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'14px',outline:'none'}}>
                    <option value="">—</option>
                    {f.options.map(o=><option key={o} value={o}>{o}</option>)}
                  </select>
                : <input type={f.type||'text'} value={form[f.id]||''} onChange={e=>setForm({...form,[f.id]:e.target.value})}
                    style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'14px',outline:'none',width:'100%',boxSizing:'border-box'}} />
              }
            </div>
          ))}
          <div style={{gridColumn:'1/-1',display:'flex',flexDirection:'column',gap:'6px'}}>
            <label style={{color:'#888',fontSize:'10px',fontWeight:'700',letterSpacing:'1px',textTransform:'uppercase'}}>Bio</label>
            <textarea value={form.bio||''} onChange={e=>setForm({...form,bio:e.target.value})} rows={3}
              style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'14px',outline:'none',resize:'vertical',width:'100%',boxSizing:'border-box'}} />
          </div>
        </div>
      </div>

      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px'}}>
        <div style={{color:gold,fontSize:'10px',letterSpacing:'3px',marginBottom:'16px',paddingBottom:'8px',borderBottom:'1px solid #1e1e1e'}}>SPONSORS ({sponsors.length}/3)</div>
        {sponsors.map(s => (
          <div key={s.id} style={{display:'flex',alignItems:'center',gap:'12px',padding:'10px 0',borderBottom:'1px solid #1a1a1a'}}>
            {s.logo_url ? <img src={`${API}${s.logo_url}`} style={{width:'40px',height:'40px',objectFit:'contain',background:'#1a1a1a',borderRadius:'3px'}} />
              : <div style={{width:'40px',height:'40px',background:'#1a1a1a',borderRadius:'3px',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'18px'}}>🎽</div>}
            <div style={{flex:1}}>
              <div style={{color:'#fff',fontWeight:'600',fontSize:'13px'}}>{s.name}</div>
              {s.website_url && <a href={s.website_url} target="_blank" style={{color:'#555',fontSize:'11px'}}>{s.website_url}</a>}
            </div>
            <button onClick={()=>deleteSponsor(s.id)} style={{background:'transparent',border:'1px solid #333',color:'#666',padding:'4px 10px',borderRadius:'3px',cursor:'pointer',fontSize:'11px'}}>✕ Remove</button>
          </div>
        ))}
        {sponsors.length < 3 && (
          <div style={{marginTop:'16px',display:'grid',gridTemplateColumns:'1fr 1fr auto',gap:'10px',alignItems:'end'}}>
            <div>
              <label style={{color:'#888',fontSize:'10px',fontWeight:'700',letterSpacing:'1px',textTransform:'uppercase',display:'block',marginBottom:'6px'}}>Sponsor Name</label>
              <input value={newSponsor.name} onChange={e=>setNewSponsor({...newSponsor,name:e.target.value})} placeholder="e.g. RedBull"
                style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'13px',outline:'none',width:'100%',boxSizing:'border-box'}} />
            </div>
            <div>
              <label style={{color:'#888',fontSize:'10px',fontWeight:'700',letterSpacing:'1px',textTransform:'uppercase',display:'block',marginBottom:'6px'}}>Website</label>
              <input value={newSponsor.website_url} onChange={e=>setNewSponsor({...newSponsor,website_url:e.target.value})} placeholder="https://..."
                style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'13px',outline:'none',width:'100%',boxSizing:'border-box'}} />
            </div>
            <button onClick={addSponsor} style={{padding:'10px 16px',background:gold,color:'#000',border:'none',borderRadius:'3px',fontSize:'12px',fontWeight:'700',cursor:'pointer',whiteSpace:'nowrap'}}>+ ADD</button>
          </div>
        )}
      </div>

      {msg && <div style={{background:'rgba(76,175,80,0.1)',border:'1px solid #4caf50',color:'#4caf50',padding:'12px 16px',borderRadius:'3px',marginBottom:'16px'}}>{msg}</div>}
      {error && <div style={{background:'rgba(255,82,82,0.1)',border:'1px solid #ff5252',color:'#ff5252',padding:'12px 16px',borderRadius:'3px',marginBottom:'16px'}}>{error}</div>}

      <button onClick={save} disabled={saving}
        style={{width:'100%',padding:'14px',background:gold,color:'#000',border:'none',borderRadius:'3px',fontSize:'13px',fontWeight:'900',letterSpacing:'2px',cursor:'pointer',textTransform:'uppercase'}}>
        {saving ? 'SAVING...' : 'SAVE PROFILE →'}
      </button>
    </Layout>
  );
}