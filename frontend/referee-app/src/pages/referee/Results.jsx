import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';
const FLAG_OPTIONS = ['OK', 'DNS', 'DNF', 'DSQ'];

export default function RefereeResults() {
  const { disciplineId } = useParams();
  const navigate = useNavigate();
  const [disc, setDisc] = useState(null);
  const [sheet, setSheet] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});
  const [saved, setSaved] = useState({});
  const [calculating, setCalculating] = useState(false);
  const [standings, setStandings] = useState([]);
  const [showStandings, setShowStandings] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get(`/competition-disciplines/${disciplineId}`),
      api.get(`/results/discipline/${disciplineId}/sheet`),
    ]).then(([discRes, sheetRes]) => {
      setDisc(discRes.data);
      setSheet(sheetRes.data);
    }).finally(() => setLoading(false));
  }, [disciplineId]);

  const updateLocal = (participantId, field, value) => {
    setSheet(prev => prev.map(p =>
      p.participant_id === participantId ? { ...p, [field]: value } : p
    ));
  };

  const save = async (participant) => {
    setSaving(s => ({ ...s, [participant.participant_id]: true }));
    try {
      await api.post(`/results/discipline/${disciplineId}`, {
        participant_id: participant.participant_id,
        primary_value: participant.primary_value !== '' && participant.primary_value != null ? parseFloat(participant.primary_value) : null,
        secondary_value: participant.secondary_value !== '' && participant.secondary_value != null ? parseFloat(participant.secondary_value) : null,
        reps: participant.reps !== '' && participant.reps != null ? parseInt(participant.reps) : null,
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

  const calculate = async () => {
    setCalculating(true);
    try {
      await api.post(`/disciplines/${disciplineId}/calculate-standings`);
      const res = await api.get(`/results/discipline/${disciplineId}/standings`);
      setStandings(res.data);
      setShowStandings(true);
    } catch (e) {
      alert('Failed to calculate standings');
    } finally {
      setCalculating(false);
    }
  };

  const isReps = disc?.discipline_mode === 'AMRAP_REPS';

  return (
    <Layout>
      {/* Breadcrumb */}
      <div style={{ marginBottom: '24px', display: 'flex', gap: '8px', color: '#555', fontSize: '13px', flexWrap: 'wrap' }}>
        <button onClick={() => navigate('/referee')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>Competitions</button>
        <span>›</span>
        {disc && (
          <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>
            Disciplines
          </button>
        )}
        <span>›</span>
        <span style={{ color: '#888' }}>{disc?.discipline_name}</span>
      </div>

      {/* Header */}
      <div style={{ marginBottom: '28px', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>{disc?.discipline_name}</h1>
          <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>
            {disc?.discipline_mode} · {sheet.length} athletes
            {disc?.time_cap_seconds ? ` · ${disc.time_cap_seconds}s cap` : ''}
            {disc?.result_unit ? ` · ${disc.result_unit}` : ''}
          </p>
        </div>
        <button
          onClick={calculate}
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
          <div style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px', marginBottom: '16px' }}>⚡ STANDINGS</div>
          {standings.sort((a, b) => a.place - b.place).map(s => {
            const athlete = sheet.find(p => p.participant_id === s.participant_id);
            return (
              <div key={s.participant_id} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '8px 0', borderBottom: '1px solid #1a1a1a' }}>
                <div style={{ color: s.place <= 3 ? gold : '#555', fontWeight: '700', width: '28px', fontSize: '15px' }}>#{s.place}</div>
                <div style={{ color: '#fff', flex: 1 }}>{athlete ? `${athlete.first_name} ${athlete.last_name}` : '—'}</div>
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
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: '200px' }}>
                <div style={{ color: gold, fontSize: '12px', fontWeight: '700', width: '32px' }}>#{p.bib_no || p.lot_number || '—'}</div>
                <div>
                  <div style={{ color: '#fff', fontWeight: '600', fontSize: '15px' }}>{p.first_name} {p.last_name}</div>
                  <div style={{ color: '#555', fontSize: '12px' }}>{p.country || '—'}</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                {isReps ? (
                  <input
                    type="number"
                    placeholder="Reps"
                    value={p.reps ?? ''}
                    onChange={e => updateLocal(p.participant_id, 'reps', e.target.value)}
                    style={{ width: '90px', padding: '9px 12px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '15px', outline: 'none' }}
                  />
                ) : (
                  <>
                    <input
                      type="number"
                      step="0.001"
                      placeholder={disc?.result_unit || 'Result'}
                      value={p.primary_value ?? ''}
                      onChange={e => updateLocal(p.participant_id, 'primary_value', e.target.value)}
                      style={{ width: '110px', padding: '9px 12px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '15px', outline: 'none' }}
                    />
                    <input
                      type="number"
                      step="0.001"
                      placeholder="Secondary"
                      value={p.secondary_value ?? ''}
                      onChange={e => updateLocal(p.participant_id, 'secondary_value', e.target.value)}
                      style={{ width: '100px', padding: '9px 12px', background: '#0a0a0a', border: '1px solid #1a1a1a', borderRadius: '3px', color: '#777', fontSize: '14px', outline: 'none' }}
                    />
                  </>
                )}
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
                    background: saved[p.participant_id] ? '#1a3a1a' : gold,
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
        {!loading && sheet.length === 0 && <p style={{ color: '#444', textAlign: 'center', padding: '40px' }}>No athletes registered.</p>}
      </div>
    </Layout>
  );
}
