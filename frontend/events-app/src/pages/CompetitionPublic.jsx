import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = 'https://api.events.worldstrongman.org';
const teal = '#005B5C';
const sand = '#E8D5B5';
const bg = '#f7f4ef';

export default function CompetitionPublic() {
  const { competitionId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/competitions/${competitionId}/live-data`)
      .then(r => setData(r.data))
      .finally(() => setLoading(false));
  }, [competitionId]);

  if (loading) return (
    <div style={{ minHeight: '100vh', background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ color: teal }}>Loading...</div>
    </div>
  );

  if (!data) return (
    <div style={{ minHeight: '100vh', background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ color: '#888' }}>Competition not found</div>
    </div>
  );

  const comp = data.competition;

  return (
    <div style={{ minHeight: '100vh', background: bg, fontFamily: 'Roboto, sans-serif' }}>
      {/* Nav */}
      <div style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '14px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => navigate('/tournaments')}>
          <div style={{ width: '32px', height: '32px', background: teal, borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '800', color: sand, fontSize: '14px' }}>W</div>
          <span style={{ fontWeight: '700', color: '#1a1a1a', fontSize: '14px' }}>WSM Events</span>
        </div>
        <button onClick={() => navigate('/login')}
          style={{ padding: '7px 16px', background: teal, color: '#fff', border: 'none', borderRadius: '6px', fontSize: '12px', fontWeight: '600', cursor: 'pointer' }}>
          Organizer Login
        </button>
      </div>

      {/* Banner */}
      {comp.banner_url ? (
        <div style={{ width: '100%', height: '280px', overflow: 'hidden' }}>
          <img src={comp.banner_url} alt={comp.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </div>
      ) : (
        <div style={{ width: '100%', height: '180px', background: `linear-gradient(135deg, ${teal}, #007a7b)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <span style={{ fontSize: '48px' }}>🏆</span>
        </div>
      )}

      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '24px', marginBottom: '32px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            {comp.logo_left_url && <img src={comp.logo_left_url} style={{ height: '60px', objectFit: 'contain' }} />}
            <div>
              <h1 style={{ fontSize: '28px', fontWeight: '900', color: '#1a1a1a', margin: '0 0 6px', textTransform: 'uppercase', letterSpacing: '1px' }}>{comp.name}</h1>
              <div style={{ color: '#888', fontSize: '14px', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                <span>📅 {comp.date_start}{comp.date_end ? ` — ${comp.date_end}` : ''}</span>
                <span>📍 {comp.city}, {comp.country}</span>
                <span style={{ color: teal, fontWeight: '600', textTransform: 'uppercase', fontSize: '12px' }}>{comp.sport_type}</span>
              </div>
            </div>
            {comp.logo_right_url && <img src={comp.logo_right_url} style={{ height: '60px', objectFit: 'contain' }} />}
          </div>
          <button onClick={() => navigate(`/tournament/${competitionId}/register`)}
            style={{ padding: '14px 28px', background: teal, color: '#fff', border: 'none', borderRadius: '6px', fontSize: '14px', fontWeight: '700', cursor: 'pointer', whiteSpace: 'nowrap' }}>
            REGISTER AS ATHLETE →
          </button>
        </div>

        {/* Description */}
        {comp.description && (
          <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '8px', padding: '20px', marginBottom: '24px' }}>
            <p style={{ color: '#555', fontSize: '14px', lineHeight: '1.7', margin: 0 }}>{comp.description}</p>
          </div>
        )}

        {/* Results per division */}
        {(data.divisions || []).map(dd => {
          const hasResults = dd.participants && dd.participants.some(p => dd.overall_standings[String(p.id)]);
          return (
            <div key={dd.division_id} style={{ marginBottom: '32px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <h2 style={{ fontSize: '16px', fontWeight: '800', color: teal, textTransform: 'uppercase', letterSpacing: '2px', margin: 0 }}>{dd.division_name}</h2>
                {hasResults && <span style={{ fontSize: '10px', fontWeight: '700', background: 'rgba(0,91,92,0.1)', color: teal, padding: '2px 8px', borderRadius: '3px' }}>RESULTS</span>}
              </div>
              {dd.participants.length === 0 ? (
                <div style={{ color: '#aaa', fontSize: '13px', padding: '16px 0' }}>No athletes registered yet</div>
              ) : (
                <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '8px', overflow: 'hidden' }}>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '500px' }}>
                      <thead>
                        <tr style={{ background: sand }}>
                          <th style={{ padding: '10px 16px', textAlign: 'center', fontSize: '11px', fontWeight: '700', letterSpacing: '1px' }}>PLACE</th>
                          <th style={{ padding: '10px 16px', textAlign: 'center', fontSize: '11px', fontWeight: '700', letterSpacing: '1px' }}>BIB</th>
                          <th style={{ padding: '10px 16px', textAlign: 'left', fontSize: '11px', fontWeight: '700', letterSpacing: '1px' }}>ATHLETE</th>
                          <th style={{ padding: '10px 16px', textAlign: 'center', fontSize: '11px', fontWeight: '700', letterSpacing: '1px' }}>COUNTRY</th>
                          {dd.disciplines.map(d => (
                            <th key={d.id} style={{ padding: '10px 8px', textAlign: 'center', fontSize: '10px', fontWeight: '700', borderLeft: '1px solid #d4c9a8' }} colSpan={2}>{d.discipline_name}</th>
                          ))}
                          <th style={{ padding: '10px 16px', textAlign: 'center', fontSize: '11px', fontWeight: '700', borderLeft: '2px solid #b8a87a' }}>TOTAL</th>
                        </tr>
                        {dd.disciplines.length > 0 && (
                          <tr style={{ background: '#f0ead8' }}>
                            <th colSpan={4}></th>
                            {dd.disciplines.map(d => (
                              <>
                                <th key={d.id+"-r"} style={{ padding: '4px 8px', textAlign: 'center', fontSize: '10px', color: '#888', borderLeft: '1px solid #d4c9a8' }}>Res</th>
                                <th key={d.id+"-p"} style={{ padding: '4px 8px', textAlign: 'center', fontSize: '10px', color: teal }}>Pts</th>
                              </>
                            ))}
                            <th></th>
                          </tr>
                        )}
                      </thead>
                      <tbody>
                        {dd.participants.map((p, idx) => {
                          const ov = dd.overall_standings[String(p.id)] || {};
                          return (
                            <tr key={p.id} style={{ borderBottom: '1px solid #eee', background: idx % 2 === 0 ? '#fff' : '#faf8f5' }}>
                              <td style={{ padding: '12px 16px', textAlign: 'center', fontWeight: '700', color: teal, fontSize: '16px' }}>{ov.overall_place || '—'}</td>
                              <td style={{ padding: '12px 16px', textAlign: 'center', fontWeight: '700' }}>{p.bib_no || '—'}</td>
                              <td style={{ padding: '12px 16px', fontWeight: '600' }}>{p.first_name} {p.last_name}</td>
                              <td style={{ padding: '12px 16px', textAlign: 'center', color: '#888' }}>{p.country || '—'}</td>
                              {dd.disciplines.map(d => {
                                const res = (dd.results_map[d.id] || {})[String(p.id)];
                                const st = (dd.standings_map[d.id] || {})[String(p.id)];
                                return (
                                  <>
                                    <td key={d.id+"-r"} style={{ padding: '12px 8px', textAlign: 'center', borderLeft: '1px solid #eee' }}>{res ? (res.reps || res.primary_value || '—') : '—'}</td>
                                    <td key={d.id+"-p"} style={{ padding: '12px 8px', textAlign: 'center', color: teal, fontWeight: '600' }}>{st ? st.points_for_discipline : '—'}</td>
                                  </>
                                );
                              })}
                              <td style={{ padding: '12px 16px', textAlign: 'center', fontWeight: '700', fontSize: '15px', borderLeft: '2px solid #e8e0d0' }}>{ov.total_points || '—'}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {/* Protocol button */}
        <div style={{ textAlign: 'center', marginTop: '32px' }}>
          <a href={`${API}/competitions/${competitionId}/protocol`} target="_blank"
            style={{ display: 'inline-block', padding: '14px 32px', background: 'transparent', border: `2px solid ${teal}`, color: teal, borderRadius: '6px', fontSize: '13px', fontWeight: '700', textDecoration: 'none', letterSpacing: '1px' }}>
            🖨️ OFFICIAL PROTOCOL PDF
          </a>
        </div>
      </div>
    </div>
  );
}
