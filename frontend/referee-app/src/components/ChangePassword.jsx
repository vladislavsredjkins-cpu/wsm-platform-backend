import { useState } from 'react';
import axios from 'axios';

const gold = '#c9a84c';
const API = 'https://ranking.worldstrongman.org';

export default function ChangePassword() {
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm: '' });
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (form.new_password !== form.confirm) { setError('Passwords do not match'); return; }
    if (form.new_password.length < 6) { setError('Min 6 characters'); return; }
    setSaving(true); setMsg(''); setError('');
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/auth/change-password`,
        { current_password: form.current_password, new_password: form.new_password },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMsg('✓ Password changed!');
      setForm({ current_password: '', new_password: '', confirm: '' });
    } catch(e) {
      setError('✗ ' + (e.response?.data?.detail || 'Failed'));
    } finally { setSaving(false); }
  };

  const inputStyle = { padding:'10px 12px', background:'#0a0a0a', border:'1px solid #2a2a2a', borderRadius:'3px', color:'#fff', fontSize:'14px', outline:'none', width:'100%', boxSizing:'border-box' };

  return (
    <div style={{background:'#111',border:'1px solid #1e1e1e',borderRadius:'4px',padding:'24px',marginBottom:'20px'}}>
      <div style={{color:gold,fontSize:'10px',letterSpacing:'3px',marginBottom:'20px',paddingBottom:'8px',borderBottom:'1px solid #1e1e1e'}}>CHANGE PASSWORD</div>
      <div style={{display:'flex',flexDirection:'column',gap:'14px'}}>
        {[
          {id:'current_password', label:'Current Password'},
          {id:'new_password', label:'New Password'},
          {id:'confirm', label:'Confirm New Password'},
        ].map(f => (
          <div key={f.id}>
            <label style={{color:'#888',fontSize:'10px',fontWeight:'700',letterSpacing:'1px',textTransform:'uppercase',display:'block',marginBottom:'6px'}}>{f.label}</label>
            <input type="password" value={form[f.id]} onChange={e=>setForm({...form,[f.id]:e.target.value})} style={inputStyle} />
          </div>
        ))}
        {msg && <div style={{color:'#4caf50',fontSize:'13px'}}>{msg}</div>}
        {error && <div style={{color:'#ff5252',fontSize:'13px'}}>{error}</div>}
        <button onClick={save} disabled={saving} style={{padding:'12px',background:gold,color:'#000',border:'none',borderRadius:'3px',fontSize:'12px',fontWeight:'900',letterSpacing:'2px',cursor:'pointer'}}>
          {saving ? 'SAVING...' : 'CHANGE PASSWORD →'}
        </button>
      </div>
    </div>
  );
}
