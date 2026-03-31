import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../AuthContext';
import { getCompetitions } from '../../api';
import Layout from '../../components/Layout';
import api from '../../api';

const COMPETITION_TYPES = [
  { value: 'INTERNATIONAL_TOURNAMENT', label: 'Exhibition Tournament', q: 1, price: 'events_single', fee: 19 },
];

export default function Competitions() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: '',
    coefficient_q: 10,
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

  const selectedType = COMPETITION_TYPES.find(t => t.value === form.competition_type) || COMPETITION_TYPES[0];

  const handleSubmit = async () => {
    if (!form.name) return alert('Name is required');
    setSaving(true);
    try {
      // Сохраняем данные формы в localStorage для использования после оплаты
      const formData = {
        name: form.name,
        coefficient_q: parseFloat(selectedType.q),
        date_start: form.date_start || null,
        date_end: form.date_end || null,
        city: form.city || null,
        country: form.country || null,
        competition_type: form.competition_type || null,
        organizer_email: form.organizer_email || null,
      };
      localStorage.setItem('pending_competition', JSON.stringify(formData));

      const res = await api.post('/payments/checkout', {
        product_type: selectedType.price,
        success_url: `https://app.ranking.worldstrongman.org/organizer/competitions?payment=success&type=competition`,
        cancel_url: `https://app.ranking.worldstrongman.org/organizer/competitions?payment=cancelled`,
        metadata: { 
          product_type: 'competition',
          competition_type: form.competition_type,
          organizer_id: user?.organizer_id || '',
        }
      });
      window.location.href = res.data.url;
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to create checkout');
    } finally {
      setSaving(false);
    }
  };

  // После возврата с Stripe — создаём соревнование
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('payment') === 'success' && params.get('type') === 'competition') {
      const pending = localStorage.getItem('pending_competition');
      if (pending) {
        const formData = JSON.parse(pending);
        localStorage.removeItem('pending_competition');
        api.post('/competitions/', formData).then(res => {
          load();
          navigate(`/organizer/competitions/${res.data.id}`);
        }).catch(() => alert('Payment successful but failed to create competition. Contact support.'));
      }
    }
    if (params.get('payment') === 'cancelled') {
      alert('Payment cancelled. Competition was not created.');
      window.history.replaceState({}, '', '/organizer/competitions');
    }
  }, []);

  return (
    <Layout>
      <div style={{ marginBottom: '28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ color: '#1a1a1a', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>Competitions</h1>
          <p style={{ color: '#888', fontSize: '13px', margin: 0 }}>Manage your competitions</p>
        </div>
        <button onClick={() => navigate('/organizer/competitions/new')} style={{ padding: '10px 24px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', letterSpacing: '1px', cursor: 'pointer' }}>
          {showForm ? 'CANCEL' : '+ NEW COMPETITION'}
        </button>
      </div>

      {/* Pricing cards */}
      {!showForm && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '12px', marginBottom: '28px' }}>
          {[
            { label: 'Add Event', types: 'Add 1 more tournament', fee: 19 },
            { label: 'Season Pass', types: '3 months unlimited', fee: 39 },
          ].map(p => (
            <div key={p.label} style={{ background: '#fff', border: '1px solid #e8e0d0', borderTop: '3px solid #005B5C', borderRadius: '8px', padding: '20px', textAlign: 'center' }}>
              <div style={{ color: '#005B5C', fontSize: '11px', fontWeight: '700', letterSpacing: '2px', marginBottom: '8px' }}>{p.label.toUpperCase()}</div>
              <div style={{ color: '#1a1a1a', fontSize: '32px', fontWeight: '900', marginBottom: '4px' }}>€{p.fee}</div>
              <div style={{ color: '#888', fontSize: '11px', lineHeight: '1.6' }}>{p.types}</div>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ color: '#005B5C', fontSize: '12px', fontWeight: '700', letterSpacing: '2px', margin: '0 0 20px' }}>NEW COMPETITION</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Competition Name</label>
              <input style={inputStyle} placeholder="WSM World Championship 2026" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            </div>
            <div>
              <label style={labelStyle}>Type</label>
              <select style={inputStyle} value={form.competition_type} onChange={e => {
                const t = COMPETITION_TYPES.find(x => x.value === e.target.value);
                setForm(f => ({ ...f, competition_type: e.target.value, coefficient_q: t?.q || 1 }));
              }}>
                {COMPETITION_TYPES.map(t => (
                  <option key={t.value} value={t.value}>{t.label} (Q={t.q})</option>
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
          {/* Price info */}
          <div style={{ marginTop: '20px', padding: '14px 18px', background: 'rgba(0,91,92,0.05)', border: '1px solid #e8e0d0', borderRadius: '3px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ color: '#888', fontSize: '11px', letterSpacing: '2px' }}>REGISTRATION FEE</div>
              <div style={{ color: '#1a1a1a', fontSize: '13px', marginTop: '4px' }}>{selectedType.label}</div>
            </div>
            <div style={{ color: '#005B5C', fontSize: '28px', fontWeight: '900' }}>€{selectedType.fee}</div>
          </div>
          <button onClick={handleSubmit} disabled={saving} style={{ marginTop: '16px', padding: '12px 32px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', letterSpacing: '1px', cursor: 'pointer' }}>
            {saving ? 'REDIRECTING...' : `PAY €${selectedType.fee} & CREATE →`}
          </button>
        </div>
      )}

      {loading && <p style={{ color: '#888' }}>Loading...</p>}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {competitions.map(c => (
          <div key={c.id}
            onClick={() => navigate(`/organizer/competitions/${c.id}`)}
            style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '18px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
            onMouseEnter={e => e.currentTarget.style.borderColor = '#005B5C'}
            onMouseLeave={e => e.currentTarget.style.borderColor = '#e8e0d0'}
          >
            <div>
              <div style={{ color: '#1a1a1a', fontWeight: '600', fontSize: '15px', marginBottom: '3px' }}>{c.name}</div>
              <div style={{ color: '#888', fontSize: '12px' }}>{c.date_start || 'No date'}{c.city ? ` · ${c.city}` : ''}{c.country ? ` · ${c.country}` : ''}</div>
            </div>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <div style={{ background: 'rgba(0,91,92,0.08)', color: '#005B5C', fontSize: '11px', fontWeight: '700', padding: '3px 8px', borderRadius: '2px' }}>Q {c.coefficient_q}</div>
              <span style={{ color: '#aaa' }}>→</span>
            </div>
          </div>
        ))}
        {!loading && competitions.length === 0 && <p style={{ color: '#888' }}>No competitions yet.</p>}
      </div>
    </Layout>
  );
}

const labelStyle = { display: 'block', color: '#666', fontSize: '11px', fontWeight: '600', letterSpacing: '1px', marginBottom: '6px' };
const inputStyle = { width: '100%', padding: '11px 14px', background: '#fff', border: '1px solid #e8e0d0', borderRadius: '3px', color: '#1a1a1a', fontSize: '14px', outline: 'none', boxSizing: 'border-box' };
