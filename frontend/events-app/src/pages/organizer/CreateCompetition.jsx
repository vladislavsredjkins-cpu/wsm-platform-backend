import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../AuthContext';
import Layout from '../../components/Layout';
import axios from 'axios';

const API = 'https://api.events.worldstrongman.org';
const teal = '#005B5C';
const sand = '#E8D5B5';

const SPORTS = [
  { key: 'strongman', label: 'Strongman', emoji: '🏋️', available: true },
  { key: 'strict_curl', label: 'Strict Curl', emoji: '💪', available: true },
  { key: 'stick_pulling', label: 'Stick Pulling', emoji: '🦯', available: true },
  { key: 'powerlifting', label: 'Powerlifting', emoji: '🏆', available: false },
];

const STRONGMAN_DISCIPLINES = [
  'Log Lift', 'Deadlift', 'Farmers Walk', 'Atlas Stones',
  'Yoke Walk', 'Car Deadlift', 'Tire Flip', 'Loading Race',
  'Overhead Press', 'Viking Press', 'Sandbag Carry', 'Keg Toss',
];

const SCORING_TYPES = [
  { value: 'max_weight', label: 'Max Weight (kg)' },
  { value: 'max_reps', label: 'Max Reps' },
  { value: 'time', label: 'Time (fastest wins)' },
  { value: 'distance', label: 'Distance (meters)' },
];

export default function CreateCompetition() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [sport, setSport] = useState(null);
  const [compForm, setCompForm] = useState({
    name: '', date_start: '', date_end: '', city: '', country: '',
  });
  const [divisions, setDivisions] = useState([]);
  const [currentDiv, setCurrentDiv] = useState({
    name: '', gender: 'male', weight_min: 80, weight_max: 140,
    age_group: 'open', format: 'individual', team_size: 3,
  });
  const [editingDiv, setEditingDiv] = useState(null);

  const steps = ['Sport', 'Details', 'Divisions', 'Review'];

  const addDivision = () => {
    if (!currentDiv.name) return;
    if (editingDiv !== null) {
      setDivisions(divisions.map((d, i) => i === editingDiv ? {...currentDiv} : d));
      setEditingDiv(null);
    } else {
      setDivisions([...divisions, {...currentDiv}]);
    }
    setCurrentDiv({ name: '', gender: 'male', weight_min: 80, weight_max: 140, age_group: 'open', format: 'individual', team_size: 3 });
  };

  const editDiv = (i) => {
    setCurrentDiv({...divisions[i]});
    setEditingDiv(i);
  };

  const removeDiv = (i) => setDivisions(divisions.filter((_, idx) => idx !== i));

  const handleCreate = async () => {
    if (!compForm.name) { setError('Competition name is required'); return; }
    if (divisions.length === 0) { setError('Add at least one division'); return; }
    setSaving(true); setError('');
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post(`${API}/competitions/`, {
        name: compForm.name,
        date_start: compForm.date_start || null,
        date_end: compForm.date_end || null,
        city: compForm.city || null,
        country: compForm.country || null,
        sport_type: sport,
      }, { headers: { Authorization: `Bearer ${token}` } });

      const compId = res.data.id;

      // Создаём divisions
      for (const div of divisions) {
        await axios.post(`${API}/divisions/`, {
          competition_id: compId,
          ...div,
        }, { headers: { Authorization: `Bearer ${token}` } });
      }

      navigate(`/organizer/competitions/${compId}`);
    } catch(e) {
      setError(e.response?.data?.detail || 'Failed to create competition');
    } finally {
      setSaving(false);
    }
  };

  const inp = { padding: '10px 12px', border: '1px solid #e8e0d0', borderRadius: '8px', fontSize: '14px', outline: 'none', background: '#fafafa', width: '100%', boxSizing: 'border-box' };
  const lbl = { display: 'block', fontSize: '11px', fontWeight: '600', color: '#666', marginBottom: '6px', letterSpacing: '0.5px', textTransform: 'uppercase' };

  return (
    <Layout>
      {/* STEPS */}
      <div style={{ display: 'flex', gap: '0', marginBottom: '32px', background: '#fff', border: '1px solid #e8e0d0', borderRadius: '10px', overflow: 'hidden' }}>
        {steps.map((s, i) => (
          <div key={i} style={{ flex: 1, padding: '12px', textAlign: 'center', fontSize: '12px', fontWeight: i === step ? '700' : '400', color: i === step ? '#fff' : i < step ? teal : '#aaa', background: i === step ? teal : i < step ? '#e8f4f0' : '#fff', borderRight: i < steps.length - 1 ? '1px solid #e8e0d0' : 'none' }}>
            {i < step ? '✓ ' : `${i + 1}. `}{s}
          </div>
        ))}
      </div>

      {/* STEP 0 — SPORT */}
      {step === 0 && (
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#1a1a1a', marginBottom: '8px' }}>Choose your sport</h2>
          <p style={{ color: '#888', fontSize: '13px', marginBottom: '24px' }}>Select the sport for this tournament</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px', marginBottom: '32px' }}>
            {SPORTS.map(s => (
              <div key={s.key} onClick={() => s.available && setSport(s.key)}
                style={{ background: sport === s.key ? '#e8f4f0' : '#fff', border: `2px solid ${sport === s.key ? teal : '#e8e0d0'}`, borderRadius: '10px', padding: '24px 16px', textAlign: 'center', cursor: s.available ? 'pointer' : 'not-allowed', opacity: s.available ? 1 : 0.5 }}>
                <div style={{ fontSize: '36px', marginBottom: '8px' }}>{s.emoji}</div>
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#1a1a1a' }}>{s.label}</div>
                {!s.available && <div style={{ fontSize: '10px', color: '#aaa', marginTop: '4px' }}>Coming Soon</div>}
              </div>
            ))}
          </div>
          <button onClick={() => sport && setStep(1)} disabled={!sport}
            style={{ padding: '12px 32px', background: sport ? teal : '#ccc', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: sport ? 'pointer' : 'not-allowed' }}>
            Next →
          </button>
        </div>
      )}

      {/* STEP 1 — DETAILS */}
      {step === 1 && (
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#1a1a1a', marginBottom: '24px' }}>Tournament details</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', maxWidth: '600px', marginBottom: '32px' }}>
            <div style={{ gridColumn: '1/-1' }}>
              <label style={lbl}>Tournament name *</label>
              <input value={compForm.name} onChange={e => setCompForm({...compForm, name: e.target.value})} placeholder="e.g. Latvia Open 2026" style={inp} />
            </div>
            <div>
              <label style={lbl}>Start date</label>
              <input type="date" value={compForm.date_start} onChange={e => setCompForm({...compForm, date_start: e.target.value})} style={inp} />
            </div>
            <div>
              <label style={lbl}>End date</label>
              <input type="date" value={compForm.date_end} onChange={e => setCompForm({...compForm, date_end: e.target.value})} style={inp} />
            </div>
            <div>
              <label style={lbl}>City</label>
              <input value={compForm.city} onChange={e => setCompForm({...compForm, city: e.target.value})} placeholder="e.g. Riga" style={inp} />
            </div>
            <div>
              <label style={lbl}>Country</label>
              <input value={compForm.country} onChange={e => setCompForm({...compForm, country: e.target.value})} placeholder="e.g. Latvia" style={inp} />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={() => setStep(0)} style={{ padding: '12px 24px', background: '#fff', border: '1px solid #e8e0d0', color: '#666', borderRadius: '8px', fontSize: '14px', cursor: 'pointer' }}>← Back</button>
            <button onClick={() => compForm.name && setStep(2)} disabled={!compForm.name}
              style={{ padding: '12px 32px', background: compForm.name ? teal : '#ccc', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: compForm.name ? 'pointer' : 'not-allowed' }}>
              Next →
            </button>
          </div>
        </div>
      )}

      {/* STEP 2 — DIVISIONS */}
      {step === 2 && (
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#1a1a1a', marginBottom: '8px' }}>Divisions</h2>
          <p style={{ color: '#888', fontSize: '13px', marginBottom: '24px' }}>Add one or more divisions. Each division has its own results table.</p>

          {/* Existing divisions */}
          {divisions.length > 0 && (
            <div style={{ marginBottom: '24px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {divisions.map((d, i) => (
                <div key={i} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '8px', padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <span style={{ fontWeight: '700', color: '#1a1a1a' }}>{d.name}</span>
                    <span style={{ color: '#888', fontSize: '12px', marginLeft: '12px' }}>{d.gender} · {d.weight_min}-{d.weight_max}kg · {d.age_group} · {d.format}{d.format === 'team' ? ` (${d.team_size} athletes)` : ''}</span>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={() => editDiv(i)} style={{ background: 'transparent', border: '1px solid #e8e0d0', color: teal, padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>Edit</button>
                    <button onClick={() => removeDiv(i)} style={{ background: 'transparent', border: '1px solid #ffcdd2', color: '#c62828', padding: '4px 10px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>✕</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Division builder */}
          <div style={{ background: '#fff', border: `1px solid ${teal}`, borderRadius: '10px', padding: '20px', marginBottom: '24px' }}>
            <div style={{ fontSize: '12px', fontWeight: '700', color: teal, marginBottom: '16px', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
              {editingDiv !== null ? 'Edit division' : '+ New division'}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div style={{ gridColumn: '1/-1' }}>
                <label style={lbl}>Division name *</label>
                <input value={currentDiv.name} onChange={e => setCurrentDiv({...currentDiv, name: e.target.value})} placeholder="e.g. Men Open 90+" style={inp} />
              </div>
              <div>
                <label style={lbl}>Gender</label>
                <select value={currentDiv.gender} onChange={e => setCurrentDiv({...currentDiv, gender: e.target.value})} style={inp}>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>
              <div>
                <label style={lbl}>Age group</label>
                <select value={currentDiv.age_group} onChange={e => setCurrentDiv({...currentDiv, age_group: e.target.value})} style={inp}>
                  <option value="open">Open</option>
                  <option value="junior">Junior (U23)</option>
                  <option value="master">Master (40+)</option>
                  <option value="master50">Master (50+)</option>
                  <option value="youth">Youth (U18)</option>
                </select>
              </div>
              <div>
                <label style={lbl}>Weight min (kg)</label>
                <input type="number" value={currentDiv.weight_min} onChange={e => setCurrentDiv({...currentDiv, weight_min: parseInt(e.target.value)})} style={inp} />
              </div>
              <div>
                <label style={lbl}>Weight max (kg)</label>
                <input type="number" value={currentDiv.weight_max} onChange={e => setCurrentDiv({...currentDiv, weight_max: parseInt(e.target.value)})} style={inp} />
              </div>
              <div>
                <label style={lbl}>Format</label>
                <select value={currentDiv.format} onChange={e => setCurrentDiv({...currentDiv, format: e.target.value})} style={inp}>
                  <option value="individual">Individual</option>
                  <option value="relay">Relay</option>
                  <option value="team">Team</option>
                </select>
              </div>
              {currentDiv.format === 'team' && (
                <div>
                  <label style={lbl}>Athletes per team</label>
                  <input type="number" min="2" max="10" value={currentDiv.team_size} onChange={e => setCurrentDiv({...currentDiv, team_size: parseInt(e.target.value)})} style={inp} />
                </div>
              )}
            </div>
            <button onClick={addDivision} disabled={!currentDiv.name}
              style={{ marginTop: '16px', padding: '10px 24px', background: currentDiv.name ? teal : '#ccc', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: '700', cursor: currentDiv.name ? 'pointer' : 'not-allowed' }}>
              {editingDiv !== null ? 'Update division' : '+ Add division'}
            </button>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={() => setStep(1)} style={{ padding: '12px 24px', background: '#fff', border: '1px solid #e8e0d0', color: '#666', borderRadius: '8px', fontSize: '14px', cursor: 'pointer' }}>← Back</button>
            <button onClick={() => divisions.length > 0 && setStep(3)} disabled={divisions.length === 0}
              style={{ padding: '12px 32px', background: divisions.length > 0 ? teal : '#ccc', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: divisions.length > 0 ? 'pointer' : 'not-allowed' }}>
              Next →
            </button>
          </div>
        </div>
      )}

      {/* STEP 3 — REVIEW */}
      {step === 3 && (
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#1a1a1a', marginBottom: '24px' }}>Review & Create</h2>
          <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '10px', padding: '24px', marginBottom: '24px' }}>
            <div style={{ display: 'grid', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '12px', borderBottom: '1px solid #f0ece4' }}>
                <span style={{ color: '#888', fontSize: '13px' }}>Sport</span>
                <span style={{ fontWeight: '600' }}>{SPORTS.find(s => s.key === sport)?.emoji} {SPORTS.find(s => s.key === sport)?.label}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '12px', borderBottom: '1px solid #f0ece4' }}>
                <span style={{ color: '#888', fontSize: '13px' }}>Tournament</span>
                <span style={{ fontWeight: '600' }}>{compForm.name}</span>
              </div>
              {compForm.date_start && <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '12px', borderBottom: '1px solid #f0ece4' }}>
                <span style={{ color: '#888', fontSize: '13px' }}>Date</span>
                <span style={{ fontWeight: '600' }}>{compForm.date_start}{compForm.date_end ? ` — ${compForm.date_end}` : ''}</span>
              </div>}
              {compForm.city && <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '12px', borderBottom: '1px solid #f0ece4' }}>
                <span style={{ color: '#888', fontSize: '13px' }}>Location</span>
                <span style={{ fontWeight: '600' }}>{compForm.city}{compForm.country ? `, ${compForm.country}` : ''}</span>
              </div>}
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#888', fontSize: '13px' }}>Divisions</span>
                <span style={{ fontWeight: '600' }}>{divisions.length} division{divisions.length > 1 ? 's' : ''}</span>
              </div>
            </div>
          </div>

          <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '10px', padding: '20px', marginBottom: '24px' }}>
            <div style={{ fontSize: '12px', fontWeight: '700', color: teal, marginBottom: '12px', textTransform: 'uppercase' }}>Divisions</div>
            {divisions.map((d, i) => (
              <div key={i} style={{ padding: '10px 0', borderBottom: i < divisions.length - 1 ? '1px solid #f0ece4' : 'none' }}>
                <div style={{ fontWeight: '600', color: '#1a1a1a' }}>{d.name}</div>
                <div style={{ fontSize: '12px', color: '#888', marginTop: '2px' }}>{d.gender} · {d.weight_min}–{d.weight_max}kg · {d.age_group} · {d.format}{d.format === 'team' ? ` · ${d.team_size} per team` : ''}</div>
              </div>
            ))}
          </div>

          {error && <div style={{ background: '#fff0f0', border: '1px solid #ffcdd2', color: '#c62828', padding: '12px 16px', borderRadius: '8px', marginBottom: '16px', fontSize: '13px' }}>{error}</div>}

          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={() => setStep(2)} style={{ padding: '12px 24px', background: '#fff', border: '1px solid #e8e0d0', color: '#666', borderRadius: '8px', fontSize: '14px', cursor: 'pointer' }}>← Back</button>
            <button onClick={handleCreate} disabled={saving}
              style={{ padding: '12px 32px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: 'pointer' }}>
              {saving ? 'Creating...' : '🚀 Create Tournament'}
            </button>
          </div>
        </div>
      )}
    </Layout>
  );
}
