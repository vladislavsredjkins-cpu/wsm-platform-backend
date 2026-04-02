import { useState, useEffect } from 'react';
import axios from 'axios';

const API = 'https://api.events.worldstrongman.org';
const authCfg = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });

export default function DrawTab({ competitionId, divisions }) {
  const [selectedDiv, setSelectedDiv] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
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
      const res = await axios.get(`${API}/competitions/${competitionId}/divisions/${selectedDiv.id}/draw`, authCfg());
      setParticipants(res.data);
    } catch {
      setParticipants([]);
    } finally {
      setLoading(false);
    }
  };

  const doDraw = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/competitions/${competitionId}/divisions/${selectedDiv.id}/draw/auto?discipline_order=1`, {}, authCfg());
      await loadDraw();
    } finally {
      setLoading(false);
    }
  };

  const saveDraw = async () => {
    await axios.patch(`${API}/competitions/${competitionId}/divisions/${selectedDiv.id}/draw`, participants.map((p, i) => ({
      participant_id: p.participant_id,
      lot_number: i + 1
    })), authCfg());
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
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #e8e0d0', flexWrap: 'wrap' }}>
        {divisions.map(d => (
          <button key={d.id} onClick={() => setSelectedDiv(d)} style={{
            padding: '8px 16px', background: 'none', border: 'none',
            color: selectedDiv?.id === d.id ? '#005B5C' : '#888',
            fontWeight: selectedDiv?.id === d.id ? '700' : '400',
            borderBottom: selectedDiv?.id === d.id ? '2px solid #005B5C' : '2px solid transparent',
            cursor: 'pointer', fontSize: '13px', marginBottom: '-1px'
          }}>{d.name || d.division_key}</button>
        ))}
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <button onClick={doDraw} style={{ padding: '9px 24px', background: '#005B5C', color: '#fff', border: 'none', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
          🎲 DRAW
        </button>
        <button onClick={saveDraw} style={{ padding: '9px 24px', background: 'transparent', border: '1px solid #005B5C', color: '#005B5C', borderRadius: '3px', fontSize: '12px', fontWeight: '700', cursor: 'pointer' }}>
          {saved ? '✓ SAVED' : '💾 SAVE'}
        </button>
        <span style={{ color: '#aaa', fontSize: '11px' }}>Drag rows to reorder manually</span>
      </div>

      {/* Table */}
      {loading ? <p style={{ color: '#888' }}>Loading...</p> : (
        <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #e8e0d0', background: '#fafafa' }}>
                {['#', 'Lot', 'Athlete', 'Country', 'Bib'].map(h => (
                  <th key={h} style={{ padding: '10px 16px', color: '#888', fontSize: '10px', letterSpacing: '2px', textAlign: h === 'Athlete' ? 'left' : 'center', fontWeight: '700' }}>{h}</th>
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
                  style={{ borderBottom: '1px solid #f0ebe3', cursor: 'grab', background: dragIdx === i ? '#f7f4ef' : '#fff' }}>
                  <td style={{ padding: '12px 16px', color: '#aaa', textAlign: 'center', fontSize: '12px' }}>{i + 1}</td>
                  <td style={{ padding: '12px 16px', color: '#005B5C', fontWeight: '700', textAlign: 'center' }}>{p.lot_number || '—'}</td>
                  <td style={{ padding: '12px 16px', color: '#1a1a1a', fontWeight: '600' }}>{p.first_name} {p.last_name}</td>
                  <td style={{ padding: '12px 16px', color: '#888', textAlign: 'center' }}>{p.country || '—'}</td>
                  <td style={{ padding: '12px 16px', color: '#888', textAlign: 'center' }}>{p.bib_no || '—'}</td>
                </tr>
              ))}
              {participants.length === 0 && (
                <tr><td colSpan="5" style={{ padding: '32px', textAlign: 'center', color: '#aaa' }}>No athletes in this division</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
