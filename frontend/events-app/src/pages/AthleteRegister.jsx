import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const teal = '#005B5C';
const API = 'https://ranking.worldstrongman.org';

const COUNTRIES = [
  'Afghanistan','Albania','Algeria','Argentina','Armenia','Australia','Austria','Azerbaijan',
  'Bahrain','Bangladesh','Belarus','Belgium','Bolivia','Bosnia & Herzegovina','Brazil','Bulgaria',
  'Canada','Chile','China','Colombia','Croatia','Czech Republic','Denmark','Egypt','Estonia',
  'Finland','France','Georgia','Germany','Ghana','Greece','Hungary','Iceland','India','Indonesia',
  'Iran','Iraq','Ireland','Israel','Italy','Japan','Jordan','Kazakhstan','Kenya','Kuwait',
  'Latvia','Lebanon','Lithuania','Malaysia','Mexico','Moldova','Mongolia','Morocco','Netherlands',
  'New Zealand','Nigeria','Norway','Pakistan','Philippines','Poland','Portugal','Romania','Russia',
  'Saudi Arabia','Serbia','Slovakia','Slovenia','South Africa','South Korea','Spain','Sweden',
  'Switzerland','Syria','Thailand','Turkey','Ukraine','United Arab Emirates','United Kingdom',
  'United States','Uzbekistan','Venezuela','Vietnam','Yemen'
];

export default function AthleteRegister() {
  const { competitionId } = useParams();
  const [competition, setCompetition] = useState(null);
  const [divisions, setDivisions] = useState([]);
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', country: '',
    bodyweight_kg: '', events_division_id: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get(`${API}/competitions/${competitionId}`).then(r => setCompetition(r.data)).catch(() => {});
    axios.get(`${API}/events-api/divisions/${competitionId}`).then(r => setDivisions(r.data)).catch(() => {});
  }, [competitionId]);

  const handle = async () => {
    setError('');
    if (!form.first_name || !form.last_name || !form.events_division_id) {
      setError('Please fill all required fields'); return;
    }
    setLoading(true);
    try {
      await axios.post(`${API}/events-api/participants`, {
        ...form,
        competition_id: competitionId,
        bodyweight_kg: form.bodyweight_kg ? parseFloat(form.bodyweight_kg) : null,
      });
      setSuccess(true);
    } catch(e) {
      setError(e.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const inp = { width: '100%', padding: '12px 14px', border: '1px solid #e8e0d0', borderRadius: '8px', fontSize: '15px', outline: 'none', boxSizing: 'border-box', background: '#fafafa' };
  const lbl = { display: 'block', fontSize: '12px', fontWeight: '600', color: '#555', marginBottom: '6px', letterSpacing: '0.5px' };

  if (success) return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ textAlign: 'center', background: '#fff', border: '1px solid #e8e0d0', borderTop: `3px solid ${teal}`, borderRadius: '12px', padding: '48px 40px', maxWidth: '420px', width: '100%' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
        <h2 style={{ fontSize: '22px', fontWeight: '800', color: '#1a1a1a', margin: '0 0 8px' }}>Registration complete!</h2>
        <p style={{ color: '#666', fontSize: '14px', margin: '0 0 24px' }}>You have been registered for <strong>{competition?.name}</strong>.</p>
        <p style={{ color: '#888', fontSize: '13px' }}>You will receive a confirmation email shortly.</p>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ width: '100%', maxWidth: '480px', background: '#fff', border: '1px solid #e8e0d0', borderTop: `3px solid ${teal}`, borderRadius: '12px', padding: '40px 32px' }}>

        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ width: '56px', height: '56px', background: teal, borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', fontSize: '24px', color: '#E8D5B5', fontWeight: '800' }}>W</div>
          <h1 style={{ fontSize: '22px', fontWeight: '800', color: '#1a1a1a', margin: '0 0 6px' }}>Athlete Registration</h1>
          {competition && <p style={{ fontSize: '14px', color: teal, fontWeight: '600', margin: 0 }}>{competition.name}</p>}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={lbl}>FIRST NAME *</label>
              <input value={form.first_name} onChange={e => setForm({...form, first_name: e.target.value})} placeholder="John" style={inp} />
            </div>
            <div>
              <label style={lbl}>LAST NAME *</label>
              <input value={form.last_name} onChange={e => setForm({...form, last_name: e.target.value})} placeholder="Smith" style={inp} />
            </div>
          </div>

          <div>
            <label style={lbl}>EMAIL</label>
            <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="you@example.com" style={inp} />
          </div>

          <div>
            <label style={lbl}>COUNTRY</label>
            <select value={form.country} onChange={e => setForm({...form, country: e.target.value})} style={{...inp, cursor: 'pointer'}}>
              <option value="">Select country</option>
              {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div>
            <label style={lbl}>BODYWEIGHT (kg)</label>
            <input type="number" step="0.1" value={form.bodyweight_kg} onChange={e => setForm({...form, bodyweight_kg: e.target.value})} placeholder="e.g. 95.5" style={inp} />
          </div>

          <div>
            <label style={lbl}>DIVISION *</label>
            <select value={form.events_division_id} onChange={e => setForm({...form, events_division_id: e.target.value})} style={{...inp, cursor: 'pointer'}}>
              <option value="">Select division</option>
              {divisions.map(d => (
                <option key={d.id} value={d.id}>
                  {d.name} {d.weight_min && d.weight_max ? `(${d.weight_min}–${d.weight_max} kg)` : ''}
                </option>
              ))}
            </select>
          </div>

          {error && <div style={{ background: '#fff0f0', border: '1px solid #ffcdd2', color: '#c62828', padding: '10px 14px', borderRadius: '8px', fontSize: '13px' }}>{error}</div>}

          <button onClick={handle} disabled={loading}
            style={{ width: '100%', padding: '14px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: loading ? 'not-allowed' : 'pointer', marginTop: '8px', opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Registering...' : 'Register →'}
          </button>

          <p style={{ fontSize: '11px', color: '#aaa', textAlign: 'center', margin: 0 }}>
            By registering you agree to our{' '}
            <a href="https://worldstrongman.org/privacy-policy" target="_blank" style={{ color: teal }}>Privacy Policy</a>
          </p>
        </div>

        <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #e8e0d0', textAlign: 'center', fontSize: '11px', color: '#ccc' }}>
          © 2026 World Strongman International Union
        </div>
      </div>
    </div>
  );
}
