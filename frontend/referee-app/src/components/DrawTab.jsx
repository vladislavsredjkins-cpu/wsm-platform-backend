import { useState, useEffect } from 'react';
import api from '../api';
const gold = '#c9a84c';

export default function DrawTab({ competitionId, divisions }) {
  const [selectedDiv, setSelectedDiv] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [disciplineOrder, setDisciplineOrder] = useState(1);
  const [dragIdx, setDragIdx] = useState(null);

  useEffect(() => {
    if (divisions.length > 0 && !selectedDiv) setSelectedDiv(divisions[0]);
  }, [divisions]);

  useEffect(() => {
    if (selectedDiv) loadDraw();
  }, [selectedDiv]);

  const loadDraw = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/competitions/${competitionId}/divisions/${selectedDiv.id}/draw`);
      setParticipants(res.data);
    } catch {
      setParticipants([]);
    } finally {
      setLoading(false);
    }
  };

  const autoDraw = async () => {
    setLoading(true);
    try {
      const res = await api.post(`/competitions/${competitionId}/divisions/${selectedDiv.id}/draw/auto?discipline_order=${disciplineOrder}`);
      await loadDraw();
    } finally {
      setLoading(false);
    }
  };

  const saveDraw = async () => {
    await api.patch(`/competitions/${competitionId}/divisions/${selectedDiv.id}/draw`, participants.map((p, i) => ({
      participant_id: p.participant_id,
      lot_number: i + 1
    })));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    await loadDraw();
  };

  const onDragStart = (i) => setDragIdx(i);
  const onDragOver = (e, i) => {
    e.preventDefault();
    if (dragIdx === null || dragIdx === i) return;
    const updated = [...participants];
    const [moved] = updated.splice(dragIdx, 1);
    updated.splice(i, 0, moved);
    setParticipants(updated);
    setDragIdx(i);
  };
  const onDragEnd = () => setDragIdx(null);

  return (
    <div>
      {/* Division selector */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #1e1e1e', paddingBottom: '0' }}>
        {divisions.map(d => (
          <button key={d.id} onClick={() => setSelectedDiv(d)} style={{
            padding: '8px 16px', background: 'none', border: 'none',
            color: selectedDiv?.id === d.id ? gold : '#555',
            fontWeight: selectedDiv?.id === d.id ? '700' : '400',
            borderBottom: selectedDiv?.id === d.id ? `2px solid ${gold}` : '2px solid transparent',
            cursor: 'pointer', fontSize: '13px'
          }}>{d.division_key}</button>
        ))}
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: '#888', fontSize: '11px', letterSpacing: '1px' }}>DISCIPLINE #</span>
          <input type="number" min="1" value={disciplineOrder} onChange={e => setDisciplineOrder(parseInt(e.target.value))}
            style={{ width: '60px', padding: '8px', background: '#0a0a0a', border: '1px solid #2a2a2a', borderRadius: '3px', color: '#fff', fontSize: '13px', outline: 'none', textAlign: 'center' }} />
        </div>
        <button onClick={autoDraw} style={{ padding: '9px 20px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
          🎲 AUTO DRAW
        </button>
        <button onClick={saveDraw} style={{ padding: '9px 20px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
          {saved ? '✓ SAVED' : '💾 SAVE ORDER'}
        </button>
        <span style={{ color: '#444', fontSize: '11px' }}>Drag rows to reorder manually</span>
      </div>

      {/* Table */}
      {loading ? <p style={{ color: '#555' }}>Loading...</p> : (
        <div style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #1e1e1e' }}>
                {['#', 'Lot', 'Athlete', 'Country', 'Bib'].map(h => (
                  <th key={h} style={{ padding: '10px 16px', color: gold, fontSize: '10px', letterSpacing: '2px', textAlign: h === 'Athlete' ? 'left' : 'center', fontWeight: '700' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {participants.map((p, i) => (
                <tr key={p.participant_id}
                  draggable
                  onDragStart={() => onDragStart(i)}
                  onDragOver={e => onDragOver(e, i)}
                  onDragEnd={onDragEnd}
                  style={{ borderBottom: '1px solid #1a1a1a', cursor: 'grab', background: dragIdx === i ? '#1a1a1a' : 'transparent' }}>
                  <td style={{ padding: '12px 16px', color: '#555', textAlign: 'center', fontSize: '12px' }}>{i + 1}</td>
                  <td style={{ padding: '12px 16px', color: gold, fontWeight: '700', textAlign: 'center' }}>{p.lot_number || '—'}</td>
                  <td style={{ padding: '12px 16px', color: '#fff', fontWeight: '600' }}>{p.first_name} {p.last_name}</td>
                  <td style={{ padding: '12px 16px', color: '#555', textAlign: 'center' }}>{p.country || '—'}</td>
                  <td style={{ padding: '12px 16px', color: '#888', textAlign: 'center' }}>{p.bib_no || '—'}</td>
                </tr>
              ))}
              {participants.length === 0 && (
                <tr><td colSpan="5" style={{ padding: '32px', textAlign: 'center', color: '#444' }}>No athletes in this division</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
