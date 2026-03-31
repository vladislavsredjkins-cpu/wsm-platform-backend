import { useState } from 'react';
import api from '../api';

const accent = '#005B5C';
const labelStyle = { display: 'block', color: '#666', fontSize: '11px', fontWeight: '600', letterSpacing: '1px', marginBottom: '6px' };
const inputStyle = { width: '100%', padding: '10px 14px', background: '#fafafa', border: '1px solid #e8e0d0', borderRadius: '4px', color: '#1a1a1a', fontSize: '13px', outline: 'none', boxSizing: 'border-box' };

const DISCIPLINES_BY_FORMAT = {
  RELAY: [
    { group: 'LIFT RELAY', items: [
      { name: 'Stone Flip',             mode: 'AMRAP_REPS' },
      { name: 'Dumbbell Lift',          mode: 'AMRAP_REPS' },
      { name: 'Axle Deadlift',          mode: 'AMRAP_REPS' },
      { name: 'Log Lift',               mode: 'AMRAP_REPS' },
    ]},
    { group: 'CARRY RELAY', items: [
      { name: 'Husafell Sandbag Carry', mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Super Yoke',             mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: "Farmer's Walk",          mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Tire Flips',             mode: 'TIME_WITH_DISTANCE_FALLBACK' },
    ]},
  ],
  CLASSIC: [
    { group: 'STANDARD', items: [
      { name: 'Stone Flip',             mode: 'AMRAP_REPS' },
      { name: 'Dumbbell Lift',          mode: 'AMRAP_REPS' },
      { name: 'Axle Deadlift',          mode: 'AMRAP_REPS' },
      { name: 'Log Lift',               mode: 'AMRAP_REPS' },
      { name: 'Husafell Sandbag Carry', mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Super Yoke',             mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: "Farmer's Walk",          mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Tire Flips',             mode: 'TIME_WITH_DISTANCE_FALLBACK' },
    ]},
    { group: 'ADDITIONAL', items: [
      { name: 'Truck Pull',             mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Car Deadlift',           mode: 'AMRAP_REPS' },
      { name: 'Columns Holding',        mode: 'STATIC_HOLD_TIME' },
      { name: 'Arm-over-Arm Pull',      mode: 'TIME_WITH_DISTANCE_FALLBACK' },
    ]},
    { group: 'CUSTOM', items: [
      { name: 'Custom', mode: 'AMRAP_REPS' },
    ]},
  ],
  PARA: [
    { group: 'PARA DISCIPLINES', items: [
      { name: 'Log Lift (Seated)',       mode: 'AMRAP_REPS' },
      { name: 'Dumbbell Lift (Seated)',  mode: 'AMRAP_REPS' },
      { name: 'Columns Holding',         mode: 'STATIC_HOLD_TIME' },
      { name: 'Harness Car Pull 15m',    mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Arm-over-Arm Pull 15m',   mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Medicine Ball Throw',     mode: 'AMRAP_DISTANCE' },
    ]},
    { group: 'CUSTOM', items: [
      { name: 'Custom', mode: 'AMRAP_REPS' },
    ]},
  ],
  TEAM_BATTLE: [
    { group: 'STANDARD', items: [
      { name: 'Stone Flip',             mode: 'AMRAP_REPS' },
      { name: 'Dumbbell Lift',          mode: 'AMRAP_REPS' },
      { name: 'Axle Deadlift',          mode: 'AMRAP_REPS' },
      { name: 'Log Lift',               mode: 'AMRAP_REPS' },
      { name: 'Husafell Sandbag Carry', mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Super Yoke',             mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: "Farmer's Walk",          mode: 'TIME_WITH_DISTANCE_FALLBACK' },
      { name: 'Tire Flips',             mode: 'TIME_WITH_DISTANCE_FALLBACK' },
    ]},
    { group: 'RELAY', items: [
      { name: 'Lift Relay',             mode: 'RELAY_DUAL_METRIC' },
      { name: 'Carry Relay',            mode: 'RELAY_DUAL_METRIC' },
    ]},
    { group: 'CUSTOM', items: [
      { name: 'Custom', mode: 'AMRAP_REPS' },
    ]},
  ],
};

const MODE_LABELS = {
  AMRAP_REPS:                  'Max Reps',
  AMRAP_DISTANCE:              'Max Distance',
  TIME_WITH_DISTANCE_FALLBACK: 'Fastest Time',
  MAX_WEIGHT_WITHIN_CAP:       'Max Weight',
  RELAY_DUAL_METRIC:           'Relay',
  STATIC_HOLD_TIME:            'Static Hold',
};

const MODE_ICONS = {
  AMRAP_REPS:                  '🔁',
  AMRAP_DISTANCE:              '📏',
  TIME_WITH_DISTANCE_FALLBACK: '⏱',
  MAX_WEIGHT_WITHIN_CAP:       '🏋️',
  RELAY_DUAL_METRIC:           '🔄',
  STATIC_HOLD_TIME:            '🕐',
};

const EMPTY_FORM = { discipline_name: '', discipline_mode: 'AMRAP_REPS', order_no: 1, time_cap_seconds: '', track_length_meters: '', implement_weight: '', notes: '' };

export default function DisciplinesTab({ divisions }) {
  const [selectedDivision, setSelectedDivision] = useState(null);
  const [disciplines, setDisciplines] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);

  const loadDisciplines = async (divisionId) => {
    const res = await api.get(`/divisions/${divisionId}/disciplines`);
    setDisciplines(res.data);
    setForm(f => ({ ...f, order_no: res.data.length + 1 }));
  };

  const selectDivision = (div) => {
    setSelectedDivision(div);
    loadDisciplines(div.id);
    setShowForm(false);
  };

  const selectTemplate = (t) => {
    setForm(f => ({ ...f, discipline_name: t.name, discipline_mode: t.mode }));
  };

  const createDiscipline = async () => {
    if (!form.discipline_name) return alert('Name required');
    setSaving(true);
    try {
      await api.post(`/divisions/${selectedDivision.id}/disciplines`, {
        discipline_name: form.discipline_name,
        discipline_mode: form.discipline_mode,
        order_no: parseInt(form.order_no) || disciplines.length + 1,
        time_cap_seconds: form.time_cap_seconds ? parseInt(form.time_cap_seconds) : null,
        track_length_meters: form.track_length_meters ? parseFloat(form.track_length_meters) : null,
        implement_weight: form.implement_weight || null,
        notes: form.notes || null,
      });
      await loadDisciplines(selectedDivision.id);
      setShowForm(false);
      setForm({ ...EMPTY_FORM, order_no: disciplines.length + 2 });
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed');
    } finally {
      setSaving(false);
    }
  };

  const deleteDiscipline = async (id) => {
    if (!confirm('Remove this discipline?')) return;
    await api.delete(`/disciplines/${id}`);
    await loadDisciplines(selectedDivision.id);
  };

  const getTemplates = () => {
    if (!selectedDivision) return [];
    return DISCIPLINES_BY_FORMAT[selectedDivision.format] || DISCIPLINES_BY_FORMAT.CLASSIC;
  };

  const needsTrack = ['TIME_WITH_DISTANCE_FALLBACK', 'AMRAP_DISTANCE', 'RELAY_DUAL_METRIC'].includes(form.discipline_mode);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: '24px' }}>
      {/* Division selector */}
      <div>
        <div style={{ color: '#888', fontSize: '11px', fontWeight: '600', letterSpacing: '1px', marginBottom: '12px' }}>DIVISION</div>
        {divisions.map(d => (
          <div key={d.id} onClick={() => selectDivision(d)}
            style={{ padding: '10px 14px', borderRadius: '4px', cursor: 'pointer', marginBottom: '4px',
              background: selectedDivision?.id === d.id ? 'rgba(0,91,92,0.08)' : '#fff',
              border: selectedDivision?.id === d.id ? `1px solid ${accent}` : '1px solid #e8e0d0',
              color: selectedDivision?.id === d.id ? accent : '#555', fontSize: '13px',
              fontWeight: selectedDivision?.id === d.id ? '600' : '400' }}>
            <div>{d.name || d.division_key}</div>
            <div style={{ fontSize: '11px', color: '#aaa', marginTop: '2px' }}>{d.format}</div>
          </div>
        ))}
        {divisions.length === 0 && <p style={{ color: '#888', fontSize: '13px' }}>No divisions yet.</p>}
      </div>

      {/* Disciplines panel */}
      <div>
        {!selectedDivision ? (
          <p style={{ color: '#888' }}>Select a division to manage disciplines.</p>
        ) : (
          <>
            <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h3 style={{ color: '#1a1a1a', margin: 0, fontSize: '16px' }}>
                {selectedDivision.name || selectedDivision.division_key}
                <span style={{ color: '#888', fontWeight: '400', fontSize: '13px' }}> ({disciplines.length}/8 · {selectedDivision.format})</span>
              </h3>
              {disciplines.length < 8 && (
                <button onClick={() => setShowForm(!showForm)}
                  style={{ padding: '7px 16px', background: showForm ? 'transparent' : accent, border: `1px solid ${accent}`, color: showForm ? accent : '#fff', borderRadius: '4px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
                  {showForm ? 'CANCEL' : '+ ADD DISCIPLINE'}
                </button>
              )}
            </div>

            {/* Add form */}
            {showForm && (
              <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '8px', padding: '20px', marginBottom: '20px' }}>
                {/* Template groups */}
                {getTemplates().map(group => (
                  <div key={group.group} style={{ marginBottom: '14px' }}>
                    <div style={{ color: '#aaa', fontSize: '10px', fontWeight: '700', letterSpacing: '1.5px', marginBottom: '8px' }}>{group.group}</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {group.items.map(t => (
                        <button key={t.name} onClick={() => selectTemplate(t)}
                          style={{ padding: '6px 12px',
                            background: form.discipline_name === t.name ? 'rgba(0,91,92,0.08)' : '#fafafa',
                            border: form.discipline_name === t.name ? `1px solid ${accent}` : '1px solid #e8e0d0',
                            color: form.discipline_name === t.name ? accent : '#555',
                            borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                          {MODE_ICONS[t.mode]} {t.name}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}

                <div style={{ borderTop: '1px solid #f0ebe3', paddingTop: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={labelStyle}>Discipline Name</label>
                    <input style={inputStyle} placeholder="e.g. Log Lift" value={form.discipline_name}
                      onChange={e => setForm(f => ({ ...f, discipline_name: e.target.value }))} />
                  </div>
                  <div>
                    <label style={labelStyle}>Scoring Mode</label>
                    <select style={inputStyle} value={form.discipline_mode}
                      onChange={e => setForm(f => ({ ...f, discipline_mode: e.target.value }))}>
                      <option value="AMRAP_REPS">🔁 Max Reps</option>
                      <option value="AMRAP_DISTANCE">📏 Max Distance</option>
                      <option value="TIME_WITH_DISTANCE_FALLBACK">⏱ Fastest Time</option>
                      <option value="MAX_WEIGHT_WITHIN_CAP">🏋️ Max Weight</option>
                      <option value="STATIC_HOLD_TIME">🕐 Static Hold</option>
                      <option value="RELAY_DUAL_METRIC">🔄 Relay</option>
                      <option value="win_loss">🏆 Win/Loss</option>
                    </select>
                  </div>
                  <div>
                    <label style={labelStyle}>Implement Weight</label>
                    <input style={inputStyle} placeholder="e.g. 100kg / 3×40/60/80kg" value={form.implement_weight}
                      onChange={e => setForm(f => ({ ...f, implement_weight: e.target.value }))} />
                  </div>
                  <div>
                    <label style={labelStyle}>Time Cap (sec)</label>
                    <input style={inputStyle} type="number" placeholder="180" value={form.time_cap_seconds}
                      onChange={e => setForm(f => ({ ...f, time_cap_seconds: e.target.value }))} />
                  </div>
                  {needsTrack && (
                    <div>
                      <label style={labelStyle}>Track Length (m)</label>
                      <input style={inputStyle} type="number" placeholder="20" value={form.track_length_meters}
                        onChange={e => setForm(f => ({ ...f, track_length_meters: e.target.value }))} />
                    </div>
                  )}
                  <div>
                    <label style={labelStyle}>Order #</label>
                    <input style={inputStyle} type="number" min="1" max="8" value={form.order_no}
                      onChange={e => setForm(f => ({ ...f, order_no: e.target.value }))} />
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <label style={labelStyle}>Notes (optional)</label>
                    <input style={inputStyle} placeholder="e.g. Farmer + Yoke combo, straps allowed" value={form.notes}
                      onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} />
                  </div>
                </div>
                <button onClick={createDiscipline} disabled={saving}
                  style={{ marginTop: '16px', padding: '10px 28px', background: accent, color: '#fff', border: 'none', borderRadius: '4px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
                  {saving ? 'ADDING...' : 'ADD DISCIPLINE →'}
                </button>
              </div>
            )}

            {/* Disciplines list */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {disciplines.map((d, i) => (
                <div key={d.id} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '14px 18px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ color: accent, fontSize: '13px', fontWeight: '700', width: '28px', textAlign: 'center' }}>
                    {d.order_no || i + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ color: '#1a1a1a', fontWeight: '600', fontSize: '14px' }}>{d.discipline_name}</div>
                    <div style={{ color: '#888', fontSize: '12px', marginTop: '3px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                      <span>{MODE_ICONS[d.discipline_mode]} {MODE_LABELS[d.discipline_mode] || d.discipline_mode}</span>
                      {d.implement_weight && <span style={{ color: accent }}>⚖️ {d.implement_weight}</span>}
                      {d.time_cap_seconds && <span>⏱ {d.time_cap_seconds}s</span>}
                      {d.track_length_meters && <span>📏 {d.track_length_meters}m</span>}
                    </div>
                    {d.notes && <div style={{ color: '#aaa', fontSize: '11px', marginTop: '4px', fontStyle: 'italic' }}>{d.notes}</div>}
                  </div>
                  <button onClick={() => deleteDiscipline(d.id)}
                    style={{ background: 'transparent', border: '1px solid #ffcdd2', color: '#c44c4c', padding: '4px 10px', borderRadius: '3px', cursor: 'pointer', fontSize: '11px' }}>
                    ✕
                  </button>
                </div>
              ))}
              {disciplines.length === 0 && <p style={{ color: '#888' }}>No disciplines yet. Add up to 8.</p>}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
