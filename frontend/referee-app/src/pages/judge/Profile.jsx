import { useState, useEffect } from 'react';
import { useAuth } from '../../AuthContext';
import Layout from '../../components/Layout';
import axios from 'axios';

const gold = '#c9a84c';
const API = 'https://ranking.worldstrongman.org';

export default function JudgeProfile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');
  const [form, setForm] = useState({});

  useEffect(() => {
    if (!user?.judge_id) return;
    axios.get(`${API}/judges/${user.judge_id}/data`)
      .then(res => { const j = res.data.judge || res.data; setProfile(j); setForm({ first_name: j.first_name||'', last_name: j.last_name||'', country: j.country||'', gender: j.gender||'', date_of_birth: j.date_of_birth||'', phone: j.phone||'', instagram: j.instagram||'', bio: j.bio||'', level: j.level||'' }); })
      .finally(() => setLoading(false));
  }, [user]);

  const save = async () => {
    setSaving(true); setMsg(''); setError('');
    try {
      const token = localStorage.getItem('token');
      await axios.patch(`${API}/judges/${user.judge_id}`, form, { headers: { Authorization: `Bearer ${token}` } });
      setMsg('Profile saved!');
    } catch(e) { setError(e.response?.data?.detail || 'Save failed'); }
    finally { setSaving(false); }
  };

  const uploadPhoto = async (file) => {
    const token = localStorage.getItem('token');
    const fd = new FormData(); fd.append('file', file);
    await axios.post(`${API}/judges/${user.judge_id}/photo`, fd, { headers: { Authorization: `Bearer ${token}` } });
    window.location.reload();
  };

  if (loading) return <Layout><p style={{color:'#555'}}>Loading...</p></Layout>;
  if (!user?.judge_id) return <Layout><p style={{color:'#ff5252'}}>No judge profile linked.</p></Layout>;

  return (
    <Layout>
      <div style={{marginBottom:'32px'}}>
        <div style={{color:gold,fontSize:'11px',letterSpacing:'3px',marginBottom:'8px'}}>JUDGE CABINET</div>
        <h1 style={{color:'#fff',fontSize:'22px',fontWeight:'700',margin:'0 0 4px'}}>My Profile</h1>
      </div>
      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px',display:'flex',alignItems:'center',gap:'20px',flexWrap:'wrap'}}>
        {profile?.photo_url ? <img src={`${API}${profile.photo_url}`} style={{width:'80px',height:'80px',borderRadius:'50%',objectFit:'cover',border:`2px solid ${gold}`}} />
          : <div style={{width:'80px',height:'80px',borderRadius:'50%',background:'#1a1a1a',border:'1px solid #2a2a2a',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'28px'}}>⚖️</div>}
        <div>
          <div style={{color:'#fff',fontWeight:'700',fontSize:'16px',marginBottom:'4px'}}>{profile?.first_name} {profile?.last_name}</div>
          <label style={{padding:'7px 16px',border:`1px solid ${gold}`,color:gold,fontSize:'11px',fontWeight:'700',cursor:'pointer',borderRadius:'3px'}}>
            📷 CHANGE PHOTO<input type="file" accept=".jpg,.jpeg,.png,.webp" style={{display:'none'}} onChange={e=>e.target.files[0]&&uploadPhoto(e.target.files[0])} />
          </label>
        </div>
      </div>
      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px'}}>
        <div style={{color:gold,fontSize:'10px',letterSpacing:'3px',marginBottom:'20px',paddingBottom:'8px',borderBottom:'1px solid #1e1e1e'}}>PERSONAL INFO</div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'14px'}}>
          {[{id:'first_name',label:'First Name'},{id:'last_name',label:'Last Name'},{id:'country',label:'Country'},{id:'gender',label:'Gender',type:'select',options:['male','female']},{id:'date_of_birth',label:'Date of Birth',type:'date'},{id:'level',label:'Judge Level',type:'select',options:['NATIONAL_1','NATIONAL_2','INTERNATIONAL_3','INTERNATIONAL_4']},{id:'phone',label:'Phone'},{id:'instagram',label:'Instagram'}].map(f => (
            <div key={f.id} style={{display:'flex',flexDirection:'column',gap:'6px'}}>
              <label style={{color:'#888',fontSize:'10px',fontWeight:'700',letterSpacing:'1px',textTransform:'uppercase'}}>{f.label}</label>
              {f.type==='select' ? <select value={form[f.id]||''} onChange={e=>setForm({...form,[f.id]:e.target.value})} style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'14px',outline:'none'}}><option value="">—</option>{f.options.map(o=><option key={o} value={o}>{o}</option>)}</select>
              : <input type={f.type||'text'} value={form[f.id]||''} onChange={e=>setForm({...form,[f.id]:e.target.value})} style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'14px',outline:'none',width:'100%',boxSizing:'border-box'}} />}
            </div>
          ))}
          <div style={{gridColumn:'1/-1',display:'flex',flexDirection:'column',gap:'6px'}}>
            <label style={{color:'#888',fontSize:'10px',fontWeight:'700',letterSpacing:'1px',textTransform:'uppercase'}}>Bio</label>
            <textarea value={form.bio||''} onChange={e=>setForm({...form,bio:e.target.value})} rows={3} style={{padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'14px',outline:'none',resize:'vertical',width:'100%',boxSizing:'border-box'}} />
          </div>
        </div>
      </div>
      {msg && <div style={{background:'rgba(76,175,80,0.1)',border:'1px solid #4caf50',color:'#4caf50',padding:'12px 16px',borderRadius:'3px',marginBottom:'16px'}}>✓ {msg}</div>}
      {error && <div style={{background:'rgba(255,82,82,0.1)',border:'1px solid #ff5252',color:'#ff5252',padding:'12px 16px',borderRadius:'3px',marginBottom:'16px'}}>✗ {error}</div>}
      <button onClick={save} disabled={saving} style={{width:'100%',padding:'14px',background:gold,color:'#000',border:'none',borderRadius:'3px',fontSize:'13px',fontWeight:'900',letterSpacing:'2px',cursor:'pointer',textTransform:'uppercase'}}>
        {saving ? 'SAVING...' : 'SAVE PROFILE →'}
      </button>
    </Layout>
  );
}