import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCompetitions } from '../../api';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';

const COMPETITION_TYPES = [
  { value: 'WORLD_CHAMPIONSHIP', label: 'World Championship', q: 10 },
  { value: 'CONTINENTAL_CHAMPIONSHIP', label: 'Continental Championship', q: 6 },
  { value: 'WORLD_CUP', label: 'World Cup', q: 4 },
  { value: 'SUBCONTINENTAL', label: 'Subcontinental', q: 2 },
  { value: 'NATIONAL_CHAMPIONSHIP', label: 'National Championship', q: 1 },
  { value: 'INTERNATIONAL_TOURNAMENT', label: 'International Tournament', q: 0.5 },
  { value: 'GRAND_PRIX', label: 'Grand Prix', q: 4 },
];

export default function Competitions() {
  const navigate = useNavigate();
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: '',
    coefficient_q: 1,
    date_start: '',
    date_end: '',
    city: '',
    country: '',
    competition_type: 'WORLD_CHAMPIONSHIP',
    organizer_email: '',
  });

  const load = () => {
    setLoading(true);
    getCompetitions()
      .then(res => setCompetitions(res.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleSubmit = async () => {
    if (!form.name) return alert('Name is required');
    setSaving(true);
    try {
      const res = await api.post('/competitions/', {
        name: form.name,
        coefficient_q: parseFloat(form.coefficient_q),
        date_start: form.date_start || null,
        date_end: form.date_end || null,
        city: form.city || null,
        country: form.country || null,
        competition_type: form.competition_type || null,
        organizer_email: form.organizer_email || null,
      });
      setShowForm(false);
      setForm({ name: '', coefficient_q: 1, date_start: '', date_end: '', city: '', country: '' });
      load();
      navigate(`/organizer/competitions/${res.data.id}`);
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to create competition');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout>
      <div style={{ marginBottom: '28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>Competitions</h1>
          <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>Manage your competitions</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} style={{ padding: '10px 24px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', letterSpacing: '1px', cursor: 'pointer' }}>
          {showForm ? 'CANCEL' : '+ NEW COMPETITION'}
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <div style={{ background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ color: gold, fontSize: '12px', fontWeight: '700', letterSpacing: '2px', margin: '0 0 20px' }}>NEW COMPETITION</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Competition Name</label>
              <input style={inputStyle} placeholder="WSM World Championship 2026" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            </div>
            <div>
              <label style={labelStyle}>Type / Q Coefficient</label>
              <select style={inputStyle} value={form.coefficient_q} onChange={e => setForm(f => ({ ...f, coefficient_q: e.target.value }))}>
                {COMPETITION_TYPES.map(t => (
                  <option key={t.value} value={t.q}>{t.label} (Q={t.q})</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelStyle}>City</label>
              <input style={inputStyle} placeholder="Dubai" value={form.city} onChange={e => setForm(f => ({ ...f, city: e.target.value }))} />
            </div>
            <div>
              <label style={labelStyle}>Country</label>
              <input style={inputStyle} placeholder="UAE" value={form.country} onChange={e => setForm(f => ({ ...f, country: e.target.value }))} />
            </div>
            <div>
              <label style={labelStyle}>Start Date</label>
              <input style={inputStyle} type="date" value={form.date_start} onChange={e => setForm(f => ({ ...f, date_start: e.target.value }))} />
            </div>
            <div>
              <label style={labelStyle}>End Date</label>
              <input style={inputStyle} type="date" value={form.date_end} onChange={e => setForm(f => ({ ...f, date_end: e.target.value }))} />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Organizer Email (visible on public page)</label>
              <input style={inputStyle} type="email" placeholder="contact@wsm.com" value={form.organizer_email} onChange={e => setForm(f => ({ ...f, organizer_email: e.target.value }))} />
            </div>
          </div>
          <button onClick={handleSubmit} disabled={saving} style={{ marginTop: '20px', padding: '12px 32px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', letterSpacing: '1px', cursor: 'pointer' }}>
            {saving ? 'CREATING...' : 'CREATE COMPETITION →'}
          </button>
        </div>
      )}

      {/* List */}
      {loading && <p style={{ color: '#555' }}>Loading...</p>}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {competitions.map(c => (
          <div key={c.id}
            onClick={() => navigate(`/organizer/competitions/${c.id}`)}
            style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '18px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
            onMouseEnter={e => e.currentTarget.style.borderColor = gold}
            onMouseLeave={e => e.currentTarget.style.borderColor = '#1e1e1e'}
          >
            <div>
              <div style={{ color: '#fff', fontWeight: '600', fontSize: '15px', marginBottom: '3px' }}>{c.name}</div>
              <div style={{ color: '#555', fontSize: '12px' }}>{c.date_start || 'No date'}{c.city ? ` · ${c.city}` : ''}{c.country ? ` · ${c.country}` : ''}</div>
            </div>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <div style={{ background: 'rgba(201,168,76,0.1)', color: gold, fontSize: '11px', fontWeight: '700', padding: '3px 8px', borderRadius: '2px' }}>Q {c.coefficient_q}</div>
              <span style={{ color: '#333' }}>→</span>
            </div>
          </div>
        ))}
        {!loading && competitions.length === 0 && <p style={{ color: '#444' }}>No competitions yet.</p>}
      </div>
    </Layout>
  );
}

const labelStyle = { display: 'block', color: '#888', fontSize: '11px', fontWeight: '600', letterSpacing: '1px', marginBottom: '6px' };
const inputStyle = { width: '100%', padding: '11px 14px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '14px', outline: 'none', boxSizing: 'border-box' };
