import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const teal = '#005B5C';
const API = 'https://api.events.worldstrongman.org';

const inp = { width: '100%', padding: '10px 14px', border: '1px solid #e8e0d0', borderRadius: '8px', fontSize: '14px', outline: 'none', boxSizing: 'border-box', background: '#fafafa' };
const lbl = { display: 'block', fontSize: '11px', fontWeight: '600', color: '#555', marginBottom: '5px', letterSpacing: '0.5px' };

export default function OrganizerProfile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [form, setForm] = useState({ name: '', country: '', city: '' });
  const [pwForm, setPwForm] = useState({ current: '', new: '', confirm: '' });
  const [pwError, setPwError] = useState('');
  const [pwSuccess, setPwSuccess] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    axios.get(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setUser(r.data))
      .catch(() => {});
    axios.get(`${API}/auth/organizer-profile`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setForm({ name: r.data.name || '', country: r.data.country || '', city: r.data.city || '' }))
      .catch(() => {});
  }, []);

  const saveProfile = async () => {
    setSaving(true);
    setSuccess(false);
    try {
      await axios.patch(`${API}/auth/profile`, form, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });
      setSuccess(true);
    } catch(e) {}
    setSaving(false);
  };

  const changePassword = async () => {
    setPwError('');
    if (pwForm.new !== pwForm.confirm) { setPwError('Passwords do not match'); return; }
    if (pwForm.new.length < 6) { setPwError('Min 6 characters'); return; }
    try {
      await axios.post(`${API}/auth/change-password`, { current_password: pwForm.current, new_password: pwForm.new }, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });
      setPwSuccess(true);
      setPwForm({ current: '', new: '', confirm: '' });
    } catch(e) { setPwError(e.response?.data?.detail || 'Error'); }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef' }}>
      <div style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '16px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '36px', height: '36px', background: teal, borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', fontWeight: '800', color: '#E8D5B5', cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>W</div>
          <span style={{ fontWeight: '700', color: '#1a1a1a', fontSize: '15px' }}>My Profile</span>
        </div>
        <div style={{ display: 'flex', gap: '16px' }}>
          <span onClick={() => navigate('/dashboard')} style={{ fontSize: '13px', color: '#666', cursor: 'pointer' }}>Dashboard</span>
          <span onClick={() => navigate('/organizer/competitions')} style={{ fontSize: '13px', color: '#666', cursor: 'pointer' }}>Competitions</span>
          <span onClick={() => { localStorage.clear(); navigate('/login'); }} style={{ fontSize: '13px', color: '#c62828', cursor: 'pointer' }}>Logout</span>
        </div>
      </div>

      <div style={{ maxWidth: '600px', margin: '40px auto', padding: '0 24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>

        {/* Account info */}
        <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '800', margin: '0 0 20px', color: '#1a1a1a' }}>Account</h2>
          <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
            <strong>Email:</strong> {user?.email}
          </div>
          <div style={{ fontSize: '14px', color: '#666' }}>
            <strong>Role:</strong> {user?.role}
          </div>
        </div>

        {/* Organization */}
        <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '800', margin: '0 0 20px', color: '#1a1a1a' }}>Organization</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={lbl}>ORGANIZATION NAME</label>
              <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="e.g. Latvia Strongman Federation" style={inp} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={lbl}>COUNTRY</label>
                <input value={form.country} onChange={e => setForm({...form, country: e.target.value})} placeholder="Latvia" style={inp} />
              </div>
              <div>
                <label style={lbl}>CITY</label>
                <input value={form.city} onChange={e => setForm({...form, city: e.target.value})} placeholder="Riga" style={inp} />
              </div>
            </div>
            {success && <div style={{ color: '#2e7d32', fontSize: '13px' }}>✅ Saved!</div>}
            <button onClick={saveProfile} disabled={saving} style={{ padding: '10px 24px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: '700', cursor: 'pointer', alignSelf: 'flex-start' }}>
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>

        {/* Change password */}
        <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '800', margin: '0 0 20px', color: '#1a1a1a' }}>Change Password</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={lbl}>CURRENT PASSWORD</label>
              <input type="password" value={pwForm.current} onChange={e => setPwForm({...pwForm, current: e.target.value})} style={inp} />
            </div>
            <div>
              <label style={lbl}>NEW PASSWORD</label>
              <input type="password" value={pwForm.new} onChange={e => setPwForm({...pwForm, new: e.target.value})} style={inp} />
            </div>
            <div>
              <label style={lbl}>CONFIRM NEW PASSWORD</label>
              <input type="password" value={pwForm.confirm} onChange={e => setPwForm({...pwForm, confirm: e.target.value})} style={inp} />
            </div>
            {pwError && <div style={{ color: '#c62828', fontSize: '13px' }}>{pwError}</div>}
            {pwSuccess && <div style={{ color: '#2e7d32', fontSize: '13px' }}>✅ Password changed!</div>}
            <button onClick={changePassword} style={{ padding: '10px 24px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: '700', cursor: 'pointer', alignSelf: 'flex-start' }}>
              Change Password
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
