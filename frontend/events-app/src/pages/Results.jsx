import { useEffect, useState } from 'react';
import api from '../api';

const gold = '#c9a84c';
const FLAG_OPTIONS = ['OK', 'DNS', 'DNF', 'DSQ'];

export default function Results({ competition, division, discipline, onBack }) {
  const [sheet, setSheet] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});
  const [saved, setSaved] = useState({});
  const [calculating, setCalculating] = useState(false);
  const [standings, setStandings] = useState([]);
  const [showStandings, setShowStandings] = useState(false);

  useEffect(() => {
    api.get(`/results/discipline/${discipline.id}/sheet`)
      .then(res => setSheet(res.data))
      .finally(() => setLoading(false));
  }, [discipline.id]);

  const updateLocal = (participantId, field, value) => {
    setSheet(prev => prev.map(p =>
      p.participant_id === participantId ? { ...p, [field]: value } : p
    ));
  };

  const save = async (participant) => {
    setSaving(s => ({ ...s, [participant.participant_id]: true }));
    try {
      await api.post(`/results/discipline/${discipline.id}`, {
        participant_id: participant.participant_id,
        primary_value: participant.primary_value ? parseFloat(participant.primary_value) : null,
        secondary_value: participant.secondary_value ? parseFloat(participant.secondary_value) : null,
        status_flag: participant.status_flag || 'OK',
      });
      setSaved(s => ({ ...s, [participant.participant_id]: true }));
      setTimeout(() => setSaved(s => ({ ...s, [participant.participant_id]: false })), 2000);
    } catch (e) {
      alert('Failed to save result');
    } finally {
      setSaving(s => ({ ...s, [participant.participant_id]: false }));
    }
  };

  const calculateStandings = async () => {
    setCalculating(true);
    try {
      await api.post(`/disciplines/${discipline.id}/calculate-standings`);
      const res = await api.get(`/results/discipline/${discipline.id}/standings`);
      setStandings(res.data);
      setShowStandings(true);
    } catch (e) {
      alert('Failed to calculate standings');
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div style={{ background: '#0a0a0a', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ background: '#111', borderBottom: '1px solid #1e1e1e', padding: '0 32px', display: 'flex', alignItems: 'center', height: '60px', gap: '12px' }}>
        <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" alt="WSM" style={{ height: '32px' }} />
        <span style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px' }}>REFEREE PORTAL</span>
      </div>

      <div style={{ padding: '32px' }}>
        <div style={{ marginBottom: '24px', display: 'flex', gap: '8px', color: '#555', fontSize: '13px', flexWrap: 'wrap' }}>
          <button onClick={() => onBack('competitions')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>Competitions</button>
          <span>›</span>
          <button onClick={() => onBack('divisions')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>{competition.name}</button>
          <span>›</span>
          <button onClick={() => onBack('disciplines')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>{division.division_key}</button>
          <span>›</span>
          <span style={{ color: '#888' }}>{discipline.discipline_name}</span>
        </div>

        <div style={{ marginBottom: '28px', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>{discipline.discipline_name}</h1>
            <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>
              {discipline.discipline_mode || 'Standard'} · {sheet.length} athletes
              {discipline.time_cap_seconds ? ` · ${discipline.time_cap_seconds}s cap` : ''}
            </p>
          </div>
          <button
            onClick={calculateStandings}
            disabled={calculating}
            style={{ padding: '10px 24px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '12px', fontWeight: '700', letterSpacing: '1px', cursor: 'pointer' }}
          >
            {calculating ? 'CALCULATING...' : '⚡ CALCULATE STANDINGS'}
          </button>
        </div>

        {loading && <p style={{ color: '#555' }}>Loading athletes...</p>}

        {/* Standings */}
        {showStandings && standings.length > 0 && (
          <div style={{ marginBottom: '32px', background: '#111', border: `1px solid ${gold}`, borderRadius: '4px', padding: '20px 24px' }}>
            <div style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px', marginBottom: '16px' }}>STANDINGS</div>
            {standings
              .sort((a, b) => a.place - b.place)
              .map(s => {
                const athlete = sheet.find(p => p.participant_id === s.participant_id);
                return (
                  <div key={s.participant_id} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '8px 0', borderBottom: '1px solid #1a1a1a' }}>
                    <div style={{ color: s.place <= 3 ? gold : '#555', fontWeight: '700', width: '28px', fontSize: '15px' }}>#{s.place}</div>
                    <div style={{ color: '#fff', flex: 1 }}>{athlete ? `${athlete.first_name} ${athlete.last_name}` : s.participant_id}</div>
                    <div style={{ color: gold, fontWeight: '600' }}>{s.points_for_discipline} pts</div>
                  </div>
                );
              })}
          </div>
        )}

        {/* Result entry */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {sheet.map((p) => (
            <div key={p.participant_id} style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '16px 20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: '180px' }}>
                  <div style={{ color: gold, fontSize: '12px', fontWeight: '700', width: '28px' }}>#{p.bib_no || '—'}</div>
                  <div>
                    <div style={{ color: '#fff', fontWeight: '600', fontSize: '15px' }}>{p.first_name} {p.last_name}</div>
                    <div style={{ color: '#555', fontSize: '12px' }}>{p.country || '—'}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                  <input
                    type="number"
                    step="0.001"
                    placeholder="Result"
                    value={p.primary_value ?? ''}
                    onChange={e => updateLocal(p.participant_id, 'primary_value', e.target.value)}
                    style={{ width: '110px', padding: '9px 12px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '15px', outline: 'none' }}
                  />
                  <select
                    value={p.status_flag || 'OK'}
                    onChange={e => updateLocal(p.participant_id, 'status_flag', e.target.value)}
                    style={{ padding: '9px 12px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '14px', outline: 'none' }}
                  >
                    {FLAG_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
                  </select>
                  <button
                    onClick={() => save(p)}
                    disabled={saving[p.participant_id]}
                    style={{
                      padding: '9px 20px',
                      background: saved[p.participant_id] ? '#2a5c2a' : gold,
                      color: saved[p.participant_id] ? '#4caf50' : '#000',
                      border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700',
                      cursor: 'pointer', letterSpacing: '1px', minWidth: '80px',
                    }}
                  >
                    {saving[p.participant_id] ? '...' : saved[p.participant_id] ? '✓ SAVED' : 'SAVE'}
                  </button>
                </div>
              </div>
            </div>
          ))}
          {!loading && sheet.length === 0 && <p style={{ color: '#444' }}>No athletes registered in this division.</p>}
        </div>
      </div>
    </div>
  );
}
