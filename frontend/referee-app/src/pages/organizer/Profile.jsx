import { useEffect, useState } from 'react';
import { useAuth } from '../../AuthContext';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';

export default function OrganizerProfile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({});
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  const [sponsors, setSponsors] = useState([]);
  const [sponsorForm, setSponsorForm] = useState({ name: '', website_url: '', tier: 'GOLD' });
  const [addingSponsors, setAddingSponsors] = useState(false);

  useEffect(() => {
    if (!user?.organizer_id) return;
    api.get(`/organizers/${user.organizer_id}/data`)
      .then(res => {
        setProfile(res.data);
        setForm({
          name: res.data.name || '',
          type: res.data.type || '',
          country: res.data.country || '',
          city: res.data.city || '',
          phone: res.data.phone || '',
          website_url: res.data.website_url || '',
          instagram: res.data.instagram || '',
        });
      })
      .catch(() => setError('Failed to load profile'));
    api.get(`/organizers/${user.organizer_id}/sponsors`)
      .then(res => setSponsors(res.data || []))
      .catch(() => {});
  }, [user]);

  const save = async () => {
    try {
      await api.patch(`/organizers/${user.organizer_id}`, form);
      setSaved(true);
      setEditing(false);
      setTimeout(() => setSaved(false), 3000);
    } catch(e) {
      setError(e.response?.data?.detail || 'Save failed');
    }
  };

  const deleteSponsor = async (sponsorId) => {
    if (!confirm('Delete this sponsor?')) return;
    await api.delete(`/organizers/${user.organizer_id}/sponsors/${sponsorId}`);
    const res = await api.get(`/organizers/${user.organizer_id}/sponsors`);
    setSponsors(res.data || []);
  };

  const addSponsor = async () => {
    if (!sponsorForm.name) return;
    await api.post(`/organizers/${user.organizer_id}/sponsors`, sponsorForm);
    const res = await api.get(`/organizers/${user.organizer_id}/sponsors`);
    setSponsors(res.data || []);
    setSponsorForm({ name: '', website_url: '', tier: 'GOLD' });
    setAddingSponsors(false);
  };

  const uploadLogo = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    await api.post(`/organizers/${user.organizer_id}/photo`, fd);
    const res = await api.get(`/organizers/${user.organizer_id}/data`);
    setProfile(res.data);
  };

  if (!user?.organizer_id) return <Layout><p style={{color:'#ff5252',padding:'32px'}}>No organizer profile linked.</p></Layout>;

  return (
    <Layout>
      <div style={{maxWidth:'700px',margin:'0 auto',padding:'32px 24px',fontFamily:'system-ui,sans-serif'}}>
        <div style={{display:'flex',alignItems:'center',gap:'24px',marginBottom:'32px',padding:'24px',background:'#111',border:'1px solid #1e1e1e',borderRadius:'6px',borderTop:`3px solid ${gold}`}}>
          <div style={{position:'relative'}}>
            {profile?.logo_url
              ? <img src={`https://ranking.worldstrongman.org${profile.logo_url}`} style={{width:'80px',height:'80px',borderRadius:'50%',objectFit:'cover',border:`2px solid ${gold}`}} />
              : <div style={{width:'80px',height:'80px',borderRadius:'50%',background:'#1e1e1e',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'32px'}}>🏛️</div>
            }
            <label style={{position:'absolute',bottom:0,right:0,background:gold,borderRadius:'50%',width:'24px',height:'24px',display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer',fontSize:'12px'}}>
              📷<input type="file" accept="image/*" onChange={uploadLogo} style={{display:'none'}} />
            </label>
          </div>
          <div>
            <div style={{color:'#fff',fontWeight:'700',fontSize:'18px'}}>{profile?.name}</div>
            <div style={{color:'#888',fontSize:'12px',marginTop:'4px'}}>{profile?.type} · {profile?.city}, {profile?.country}</div>
            <div style={{color:gold,fontSize:'11px',marginTop:'4px',letterSpacing:'1px'}}>ORGANIZER</div>
          </div>
        </div>

        {error && <div style={{background:'rgba(255,82,82,0.1)',border:'1px solid rgba(255,82,82,0.3)',color:'#ff5252',padding:'10px 14px',borderRadius:'3px',marginBottom:'16px'}}>{error}</div>}
        {saved && <div style={{background:'rgba(76,175,80,0.1)',border:'1px solid rgba(76,175,80,0.3)',color:'#4caf50',padding:'10px 14px',borderRadius:'3px',marginBottom:'16px'}}>✓ Saved</div>}

        <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'6px',padding:'24px'}}>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'20px'}}>
            <div style={{color:gold,fontSize:'10px',letterSpacing:'3px'}}>ORGANIZATION INFO</div>
            {!editing
              ? <button onClick={() => setEditing(true)} style={{background:'transparent',border:`1px solid ${gold}`,color:gold,padding:'6px 16px',borderRadius:'3px',fontSize:'11px',cursor:'pointer'}}>EDIT</button>
              : <div style={{display:'flex',gap:'8px'}}>
                  <button onClick={save} style={{background:gold,border:'none',color:'#000',padding:'6px 16px',borderRadius:'3px',fontSize:'11px',fontWeight:'700',cursor:'pointer'}}>SAVE</button>
                  <button onClick={() => setEditing(false)} style={{background:'transparent',border:'1px solid #333',color:'#555',padding:'6px 16px',borderRadius:'3px',fontSize:'11px',cursor:'pointer'}}>CANCEL</button>
                </div>
            }
          </div>

          {[
            ['name','Organization Name'],
            ['type','Type'],
            ['country','Country'],
            ['city','City'],
            ['phone','Phone'],
            ['website_url','Website'],
            ['instagram','Instagram'],
          ].map(([field, label]) => (
            <div key={field} style={{marginBottom:'16px'}}>
              <div style={{color:'#555',fontSize:'10px',letterSpacing:'2px',marginBottom:'6px'}}>{label}</div>
              {editing
                ? <input value={form[field]||''} onChange={e => setForm({...form,[field]:e.target.value})}
                    style={{width:'100%',padding:'10px 12px',background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'14px'}} />
                : <div style={{color:'#fff',fontSize:'14px'}}>{profile?.[field] || <span style={{color:'#333'}}>—</span>}</div>
              }
            </div>
          ))}
        </div>
      </div>
      <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'6px',padding:'24px',marginTop:'20px'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'16px'}}>
          <div style={{color:gold,fontSize:'10px',letterSpacing:'3px'}}>SPONSORS</div>
          <button onClick={() => setAddingSponsors(!addingSponsors)} style={{background:'transparent',border:`1px solid ${gold}`,color:gold,padding:'6px 16px',borderRadius:'3px',fontSize:'11px',cursor:'pointer'}}>+ ADD</button>
        </div>
        {addingSponsors && (
          <div style={{background:'#0a0a0a',border:'1px solid #2a2a2a',borderRadius:'4px',padding:'16px',marginBottom:'16px'}}>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'12px',marginBottom:'12px'}}>
              <input placeholder="Sponsor name" value={sponsorForm.name} onChange={e => setSponsorForm({...sponsorForm,name:e.target.value})}
                style={{padding:'8px 12px',background:'#111',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'13px'}} />
              <select value={sponsorForm.tier} onChange={e => setSponsorForm({...sponsorForm,tier:e.target.value})}
                style={{padding:'8px 12px',background:'#111',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'13px'}}>
                <option value="TITLE">TITLE</option>
                <option value="GOLD">GOLD</option>
                <option value="SILVER">SILVER</option>
                <option value="BRONZE">BRONZE</option>
              </select>
              <input placeholder="Website URL" value={sponsorForm.website_url} onChange={e => setSponsorForm({...sponsorForm,website_url:e.target.value})}
                style={{padding:'8px 12px',background:'#111',border:'1px solid #2a2a2a',borderRadius:'3px',color:'#fff',fontSize:'13px'}} />
            </div>
            <button onClick={addSponsor} style={{background:gold,border:'none',color:'#000',padding:'8px 20px',borderRadius:'3px',fontSize:'11px',fontWeight:'700',cursor:'pointer'}}>SAVE SPONSOR</button>
          </div>
        )}
        {sponsors.length === 0
          ? <div style={{color:'#333',fontSize:'13px'}}>No sponsors yet</div>
          : <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(160px,1fr))',gap:'12px'}}>
              {sponsors.map(s => (
                <div key={s.id} style={{background:'#0a0a0a',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'12px',textAlign:'center'}}>
                  <label style={{cursor:'pointer',display:'block',marginBottom:'8px'}}>
                    {s.logo_url
                      ? <img src={`https://ranking.worldstrongman.org${s.logo_url}`} style={{height:'80px',objectFit:'contain',maxWidth:'100%'}} />
                      : <div style={{height:'80px',display:'flex',alignItems:'center',justifyContent:'center',color:'#333',fontSize:'10px',border:'1px dashed #333',borderRadius:'3px'}}>+ LOGO</div>
                    }
                    <input type="file" accept="image/*" style={{display:'none'}} onChange={async e => {
                      const fd = new FormData(); fd.append('file', e.target.files[0]);
                      await api.post(`/organizers/${user.organizer_id}/sponsors/${s.id}/logo`, fd);
                      const res = await api.get(`/organizers/${user.organizer_id}/sponsors`);
                      setSponsors(res.data || []);
                    }} />
                  </label>
                  <div style={{color:'#fff',fontSize:'12px',fontWeight:'700'}}>{s.name}</div>
                  {s.website_url && <a href={s.website_url} target="_blank" style={{color:gold,fontSize:'10px',display:'block',marginTop:'4px'}}>{s.website_url}</a>}
                  <button onClick={() => deleteSponsor(s.id)} style={{marginTop:'8px',background:'transparent',border:'1px solid #ff5252',color:'#ff5252',padding:'3px 8px',borderRadius:'3px',fontSize:'10px',cursor:'pointer',width:'100%'}}>✕ REMOVE</button>
                </div>
              ))}
            </div>
        }
      </div>
    </Layout>
  );
}
