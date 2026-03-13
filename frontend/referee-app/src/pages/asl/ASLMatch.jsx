import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import api from '../../api';
import { useAuth } from '../../AuthContext';

const gold = '#c9a84c';

const DISCIPLINES = [
  { name: 'Stone Flip',             unit: 'reps', result_type: 'higher_wins' },
  { name: 'Dumbbell Lift',          unit: 'reps', result_type: 'higher_wins' },
  { name: 'Axle Deadlift',          unit: 'reps', result_type: 'higher_wins' },
  { name: 'Log Lift',               unit: 'reps', result_type: 'higher_wins' },
  { name: 'Husafell Sandbag Carry', unit: 'sec',  result_type: 'lower_wins'  },
  { name: 'Super Yoke',             unit: 'sec',  result_type: 'lower_wins'  },
  { name: "Farmer's Walk",          unit: 'sec',  result_type: 'lower_wins'  },
  { name: 'Tire Flips',             unit: 'sec',  result_type: 'lower_wins'  },
];

export default function ASLMatch() {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [match, setMatch] = useState(null);
  const [homeTeam, setHomeTeam] = useState(null);
  const [awayTeam, setAwayTeam] = useState(null);
  const [results, setResults] = useState({});
  const [inputs, setInputs] = useState({});
  const [saving, setSaving] = useState(null);
  const [mySide, setMySide] = useState(null); // 'home' | 'away' | null (admin sees both)

  const isAdmin = user?.role === 'WSM_ADMIN' || user?.role === 'ORGANIZER';

  useEffect(() => {
    api.get(`/api/asl/matches/${matchId}`).then(async r => {
      const m = r.data;
      setMatch(m);

      const [ht, at, dr] = await Promise.all([
        api.get(`/teams/${m.home_team_id}`),
        api.get(`/teams/${m.away_team_id}`),
        api.get(`/api/asl/matches/${matchId}/disciplines`),
      ]);
      setHomeTeam(ht.data);
      setAwayTeam(at.data);

      const res = {};
      const inp = {};
      dr.data.forEach(d => {
        res[d.discipline_name] = d;
        inp[d.discipline_name] = { home: d.home_result, away: d.away_result };
      });
      setResults(res);
      setInputs(inp);

      // Определяем сторону судьи
      if (!isAdmin) {
        // Получаем my matches чтобы узнать my_side
        try {
          const myMatches = await api.get('/api/asl/matches/my');
          const myMatch = myMatches.data.find(mm => mm.id === matchId);
          if (myMatch) setMySide(myMatch.my_side);
        } catch {}
      }
    });
  }, [matchId]);

  const saveResult = async (disc) => {
    const val = inputs[disc.name] || {};
    const homeVal = mySide === 'away' ? null : parseFloat(val.home) || 0;
    const awayVal = mySide === 'home' ? null : parseFloat(val.away) || 0;
    if (mySide === 'home' && !val.home) return;
    if (mySide === 'away' && !val.away) return;
    if (!mySide && !val.home && !val.away) return;

    setSaving(disc.name);
    const payload = {
      discipline_name: disc.name,
      result_type: disc.result_type,
      unit: disc.unit,
    };
    if (mySide === 'home' || isAdmin || !mySide) payload.home_result = parseFloat(val.home) || 0;
    if (mySide === 'away' || isAdmin || !mySide) payload.away_result = parseFloat(val.away) || 0;

    const res = await api.post(`/api/asl/matches/${matchId}/disciplines`, payload);
    const updated = await api.get(`/api/asl/matches/${matchId}/disciplines`);
    const newRes = {};
    updated.data.forEach(d => { newRes[d.discipline_name] = d; });
    setResults(newRes);
    setMatch(prev => ({ ...prev, home_score: res.data.home_score, away_score: res.data.away_score }));
    setSaving(null);
  };

  const getWinnerColor = (winner, side) => {
    if (winner === side) return '#4caf50';
    if (winner === 'draw') return gold;
    if (winner) return '#ff5252';
    return '#fff';
  };

  const showHome = isAdmin || !mySide || mySide === 'home';

  const printProtocol = () => {
    const win = window.open('', '_blank', 'width=900,height=700');
    const disciplineRows = DISCIPLINES.map((disc, i) => {
      const r = results[disc.name];
      const winner = r?.winner === 'home' ? homeTeam?.name : r?.winner === 'away' ? awayTeam?.name : r?.winner === 'draw' ? 'DRAW' : '—';
      const winnerColor = r?.winner === 'home' ? '#1a7a1a' : r?.winner === 'away' ? '#1a1a7a' : '#000';
      return `<tr style="border-bottom:1px solid #ddd">
        <td style="padding:10px 8px;text-align:center;color:#666">${i+1}</td>
        <td style="padding:10px 8px;font-weight:700;font-size:14px">${disc.name}</td>
        <td style="padding:10px 8px;text-align:center;font-size:13px;color:#333">${disc.result_type === 'lower_wins' ? '⬇ lower wins' : '⬆ higher wins'}</td>
        <td style="padding:10px 8px;text-align:center;font-weight:700;font-size:15px">${r ? r.home_result + ' ' + disc.unit : '—'}</td>
        <td style="padding:10px 8px;text-align:center;font-weight:700;font-size:15px">${r ? r.away_result + ' ' + disc.unit : '—'}</td>
        <td style="padding:10px 8px;text-align:center;font-weight:800;color:${winnerColor}">${winner}</td>
      </tr>`;
    }).join('');

    win.document.write(`<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Match Protocol</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: Arial, sans-serif; color: #000; background: #fff; padding: 20px; }
    @page { margin: 15mm; size: A4; }
    @media print { body { padding: 0; } }
  </style>
</head>
<body>
  <!-- Header -->
  <div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:16px;border-bottom:3px solid #000;margin-bottom:20px">
    <img src="https://ranking.worldstrongman.org/static/wsm_logo.png" style="height:70px;object-fit:contain" />
    <div style="text-align:center">
      <div style="font-size:22px;font-weight:900;letter-spacing:2px">OFFICIAL MATCH PROTOCOL</div>
      <div style="font-size:13px;color:#555;margin-top:4px">Asian Strongman League · Round ${match?.round_number} · ${match?.match_date || ''}</div>
    </div>
    <img src="https://ranking.worldstrongman.org/static/asia_strongman.png" style="height:70px;object-fit:contain" />
  </div>

  <!-- Teams & Score -->
  <div style="display:flex;align-items:center;justify-content:center;gap:40px;margin-bottom:20px;padding:16px;border:2px solid #000;border-radius:6px">
    <div style="text-align:center;flex:1">
      ${homeTeam?.logo_url ? `<img src="https://ranking.worldstrongman.org${homeTeam.logo_url}" style="height:50px;object-fit:contain;margin-bottom:6px" /><br>` : ''}
      <div style="font-size:20px;font-weight:900">${homeTeam?.name || '—'}</div>
      <div style="font-size:11px;color:#666;letter-spacing:2px">HOME</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:40px;font-weight:900;letter-spacing:8px">${match?.home_score} : ${match?.away_score}</div>
      <div style="font-size:11px;color:#666;margin-top:4px">${match?.status === 'completed' ? '✓ COMPLETED' : 'IN PROGRESS'}</div>
    </div>
    <div style="text-align:center;flex:1">
      ${awayTeam?.logo_url ? `<img src="https://ranking.worldstrongman.org${awayTeam.logo_url}" style="height:50px;object-fit:contain;margin-bottom:6px" /><br>` : ''}
      <div style="font-size:20px;font-weight:900">${awayTeam?.name || '—'}</div>
      <div style="font-size:11px;color:#666;letter-spacing:2px">AWAY</div>
    </div>
  </div>

  <!-- Judges -->
  <div style="display:flex;justify-content:space-between;margin-bottom:20px;padding:10px 16px;background:#f5f5f5;border-radius:4px">
    <div><span style="font-size:10px;color:#888;letter-spacing:1px">JUDGE 1 (HOME):</span> <strong>${match?.judge1_name || 'Not assigned'}</strong></div>
    <div><span style="font-size:10px;color:#888;letter-spacing:1px">JUDGE 2 (AWAY):</span> <strong>${match?.judge2_name || 'Not assigned'}</strong></div>
  </div>

  <!-- Disciplines Table -->
  <table style="width:100%;border-collapse:collapse;margin-bottom:32px">
    <thead>
      <tr style="background:#000;color:#fff">
        <th style="padding:10px 8px;text-align:center;width:40px">#</th>
        <th style="padding:10px 8px;text-align:left">Discipline</th>
        <th style="padding:10px 8px;text-align:center">Rule</th>
        <th style="padding:10px 8px;text-align:center">${homeTeam?.name || 'HOME'}</th>
        <th style="padding:10px 8px;text-align:center">${awayTeam?.name || 'AWAY'}</th>
        <th style="padding:10px 8px;text-align:center">Winner</th>
      </tr>
    </thead>
    <tbody>${disciplineRows}</tbody>
  </table>

  <!-- Signatures -->
  <div style="display:flex;justify-content:space-between;margin-top:48px">
    <div style="text-align:center;min-width:160px">
      <div style="border-top:1px solid #000;padding-top:8px;margin-top:40px">
        <div style="font-size:11px;color:#666">Judge 1 (Home)</div>
        <div style="font-size:13px;font-weight:700;margin-top:2px">${match?.judge1_name || '_______________'}</div>
      </div>
    </div>
    <div style="text-align:center;min-width:160px">
      <div style="border-top:1px solid #000;padding-top:8px;margin-top:40px">
        <div style="font-size:11px;color:#666">Judge 2 (Away)</div>
        <div style="font-size:13px;font-weight:700;margin-top:2px">${match?.judge2_name || '_______________'}</div>
      </div>
    </div>
    <div style="text-align:center;min-width:160px">
      <div style="border-top:1px solid #000;padding-top:8px;margin-top:40px">
        <div style="font-size:11px;color:#666">Organizer</div>
        <div style="font-size:13px;margin-top:2px">_______________</div>
      </div>
    </div>
  </div>

  <script>window.onload = () => { window.print(); }</script>
</body>
</html>`);
    win.document.close();
  };

  // Print styles
  const printStyles = `
    @media print {
      @page { margin: 15mm; size: A4; }
      body { background: white !important; color: black !important; font-family: Arial, sans-serif; }
      .no-print, nav, header { display: none !important; }
      .print-only { display: block !important; }
      .screen-only { display: none !important; }
      * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }
    @media screen {
      .print-only { display: none !important; }
    }
  `;
  const showAway = isAdmin || !mySide || mySide === 'away';

  return (
    <Layout>
      <style>{printStyles}</style>
      {/* Print Header — скрыт на экране, виден при печати */}
      <div className="print-header" style={{ display: 'none', flexDirection: 'column', alignItems: 'center', marginBottom: '24px', borderBottom: '2px solid #000', paddingBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', marginBottom: '16px' }}>
          <img src="https://ranking.worldstrongman.org/static/wsm_logo.png" style={{ height: '70px', objectFit: 'contain' }} />
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '20px', fontWeight: '900', letterSpacing: '3px', color: '#000' }}>OFFICIAL MATCH PROTOCOL</div>
            <div style={{ fontSize: '13px', color: '#444', marginTop: '4px' }}>Asian Strongman League</div>
            {match && <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>Round {match.round_number} · {match.match_date}</div>}
          </div>
          <img src="https://ranking.worldstrongman.org/static/asia_strongman.png" style={{ height: '70px', objectFit: 'contain' }} />
        </div>
        {/* Teams */}
        {match && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '32px', marginBottom: '8px' }}>
            <div style={{ textAlign: 'center' }}>
              {homeTeam?.logo_url && <img src={`https://ranking.worldstrongman.org${homeTeam.logo_url}`} style={{ height: '50px', objectFit: 'contain' }} />}
              <div style={{ fontSize: '16px', fontWeight: '800' }}>{homeTeam?.name}</div>
              <div style={{ fontSize: '11px', color: '#666' }}>HOME</div>
            </div>
            <div style={{ fontSize: '32px', fontWeight: '900' }}>{match.home_score} : {match.away_score}</div>
            <div style={{ textAlign: 'center' }}>
              {awayTeam?.logo_url && <img src={`https://ranking.worldstrongman.org${awayTeam.logo_url}`} style={{ height: '50px', objectFit: 'contain' }} />}
              <div style={{ fontSize: '16px', fontWeight: '800' }}>{awayTeam?.name}</div>
              <div style={{ fontSize: '11px', color: '#666' }}>AWAY</div>
            </div>
          </div>
        )}
        {/* Judges */}
        {match && (
          <div style={{ display: 'flex', gap: '48px', fontSize: '12px', color: '#444' }}>
            <div>Judge 1 (Home): <strong>{match.judge1_name || '—'}</strong></div>
            <div>Judge 2 (Away): <strong>{match.judge2_name || '—'}</strong></div>
          </div>
        )}
      </div>
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ color: '#555', fontSize: '12px', marginBottom: '8px', cursor: 'pointer' }} onClick={() => navigate(-1)}>← Back</div>
            <div style={{ color: gold, fontSize: '11px', letterSpacing: '3px', marginBottom: '6px' }}>
              MATCH PROTOCOL {mySide && <span style={{ color: '#555' }}>· YOU: {mySide.toUpperCase()} SIDE</span>}
            </div>
          </div>
          <a href="https://ranking.worldstrongman.org/asl/match-help" target="_blank" style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #333', color: '#555', borderRadius: '3px', fontSize: '11px', fontWeight: '700', letterSpacing: '1px', textDecoration: 'none' }}>📖 MATCH HELP</a>
          {isAdmin && (
            <button onClick={() => printProtocol()}
              style={{ padding: '8px 20px', background: 'transparent', border: `1px solid ${gold}`, color: gold, borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer', letterSpacing: '1px' }}>
              🖨 PRINT
            </button>
          )}
        </div>
      </div>

      {/* Score header */}
      {match && (
        <div style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '24px', marginBottom: '24px', textAlign: 'center' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', alignItems: 'center', gap: '24px' }}>
            <div style={{ textAlign: 'right' }}>
              {homeTeam?.logo_url && <img src={`https://ranking.worldstrongman.org${homeTeam.logo_url}`} style={{ width: '48px', height: '48px', objectFit: 'contain', marginBottom: '8px' }} />}
              <div style={{ color: mySide === 'home' ? gold : '#fff', fontWeight: '700', fontSize: '18px' }}>{homeTeam?.name || '—'}</div>
              <div style={{ color: '#555', fontSize: '11px' }}>HOME {mySide === 'home' && '👤'}</div>
            </div>
            <div style={{ background: '#1a1a1a', border: `1px solid ${gold}`, borderRadius: '8px', padding: '12px 28px' }}>
              <div style={{ color: gold, fontWeight: '900', fontSize: '36px', letterSpacing: '8px' }}>
                {match.home_score} : {match.away_score}
              </div>
              <div style={{ color: match.status === 'completed' ? '#4caf50' : '#555', fontSize: '10px', letterSpacing: '2px', marginTop: '4px' }}>
                {match.status === 'completed' ? '✓ COMPLETED' : 'IN PROGRESS'}
              </div>
            </div>
            <div style={{ textAlign: 'left' }}>
              {awayTeam?.logo_url && <img src={`https://ranking.worldstrongman.org${awayTeam.logo_url}`} style={{ width: '48px', height: '48px', objectFit: 'contain', marginBottom: '8px' }} />}
              <div style={{ color: mySide === 'away' ? gold : '#fff', fontWeight: '700', fontSize: '18px' }}>{awayTeam?.name || '—'}</div>
              <div style={{ color: '#555', fontSize: '11px' }}>AWAY {mySide === 'away' && '👤'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Judges & Match Info */}
      {match && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '24px' }}>
          <div style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '14px 18px' }}>
            <div style={{ color: '#555', fontSize: '9px', letterSpacing: '2px', marginBottom: '6px' }}>JUDGE 1 · HOME</div>
            <div style={{ color: match.judge1_name ? '#fff' : '#333', fontSize: '13px', fontWeight: '600' }}>
              {match.judge1_name || 'Not assigned'}
            </div>
            {match.judge1_name && <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#4caf50', marginTop: '6px' }} />}
          </div>
          <div style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '14px 18px', textAlign: 'center' }}>
            <div style={{ color: '#555', fontSize: '9px', letterSpacing: '2px', marginBottom: '6px' }}>MATCH INFO</div>
            <div style={{ color: '#888', fontSize: '12px' }}>Round {match.round_number}</div>
            {match.match_date && <div style={{ color: '#555', fontSize: '11px', marginTop: '4px' }}>{match.match_date}</div>}
          </div>
          <div style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '14px 18px', textAlign: 'right' }}>
            <div style={{ color: '#555', fontSize: '9px', letterSpacing: '2px', marginBottom: '6px' }}>JUDGE 2 · AWAY</div>
            <div style={{ color: match.judge2_name ? '#fff' : '#333', fontSize: '13px', fontWeight: '600' }}>
              {match.judge2_name || 'Not assigned'}
            </div>
            {match.judge2_name && <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#4caf50', marginTop: '6px', marginLeft: 'auto' }} />}
          </div>
        </div>
      )}

      {/* Disciplines */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {DISCIPLINES.map((disc, i) => {
          const r = results[disc.name];
          const inp = inputs[disc.name] || {};
          return (
            <div key={disc.name} style={{ background: '#111', border: `1px solid ${r ? '#2a2a2a' : '#1e1e1e'}`, borderRadius: '4px', padding: '16px 20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: `${showHome ? '1fr' : ''} auto ${showAway ? '1fr' : ''}`, alignItems: 'center', gap: '16px' }}>

                {/* Home result */}
                {showHome && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'flex-end' }}>
                    <div style={{ textAlign: 'right' }}>
                      {r && <div style={{ color: getWinnerColor(r.winner, 'home'), fontWeight: '700', fontSize: '18px' }}>{r.home_result} {disc.unit}</div>}
                      <div style={{ color: '#555', fontSize: '9px', textAlign: 'center', marginBottom: '3px' }}>HOME</div>
                      <input
                        type="number" step="0.01" placeholder={disc.unit}
                        value={inp.home || ''}
                        onChange={e => setInputs(prev => ({ ...prev, [disc.name]: { ...prev[disc.name], home: e.target.value } }))}
                        style={{ width: '100px', padding: '8px', background: '#0a0a0a', border: `1px solid ${mySide === 'home' ? gold : '#2a2a2a'}`, borderRadius: '3px', color: '#fff', fontSize: '14px', textAlign: 'center', outline: 'none' }}
                      />
                    </div>
                  </div>
                )}

                {/* Discipline info */}
                <div style={{ textAlign: 'center', minWidth: '160px' }}>
                  <div style={{ color: '#555', fontSize: '10px', marginBottom: '4px' }}>#{i + 1}</div>
                  <div style={{ color: gold, fontWeight: '700', fontSize: '14px' }}>{disc.name}</div>
                  <div style={{ color: '#444', fontSize: '10px', marginTop: '2px' }}>{disc.result_type === 'lower_wins' ? '⬇ lower wins' : '⬆ higher wins'}</div>
                  {r?.winner && (
                    <div style={{ marginTop: '6px', color: r.winner === 'draw' ? gold : '#4caf50', fontSize: '11px', fontWeight: '700' }}>
                      {r.winner === 'draw' ? 'DRAW' : r.winner === 'home' ? `${homeTeam?.name || 'HOME'} wins` : `${awayTeam?.name || 'AWAY'} wins`}
                    </div>
                  )}
                  <button onClick={() => saveResult(disc)} disabled={saving === disc.name}
                    style={{ marginTop: '8px', padding: '5px 14px', background: gold, color: '#000', border: 'none', borderRadius: '3px', fontSize: '10px', fontWeight: '700', cursor: 'pointer', opacity: saving === disc.name ? 0.6 : 1 }}>
                    {saving === disc.name ? '...' : 'SAVE'}
                  </button>
                </div>

                {/* Away result */}
                {showAway && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div>
                      {r && <div style={{ color: getWinnerColor(r.winner, 'away'), fontWeight: '700', fontSize: '18px' }}>{r.away_result} {disc.unit}</div>}
                      <div style={{ color: '#555', fontSize: '9px', textAlign: 'center', marginBottom: '3px' }}>AWAY</div>
                      <input
                        type="number" step="0.01" placeholder={disc.unit}
                        value={inp.away || ''}
                        onChange={e => setInputs(prev => ({ ...prev, [disc.name]: { ...prev[disc.name], away: e.target.value } }))}
                        style={{ width: '100px', padding: '8px', background: '#0a0a0a', border: `1px solid ${mySide === 'away' ? gold : '#2a2a2a'}`, borderRadius: '3px', color: '#fff', fontSize: '14px', textAlign: 'center', outline: 'none' }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      {/* Print Results Table */}
      {isAdmin && (
        <div className="print-header" style={{ display: 'none', marginTop: '24px', borderTop: '1px solid #ccc', paddingTop: '16px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #000' }}>
                <th style={{ padding: '8px', textAlign: 'left' }}>#</th>
                <th style={{ padding: '8px', textAlign: 'left' }}>Discipline</th>
                <th style={{ padding: '8px', textAlign: 'center' }}>Home Result</th>
                <th style={{ padding: '8px', textAlign: 'center' }}>Away Result</th>
                <th style={{ padding: '8px', textAlign: 'center' }}>Winner</th>
              </tr>
            </thead>
            <tbody>
              {DISCIPLINES.map((disc, i) => {
                const r = results[disc.name];
                return (
                  <tr key={disc.name} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '8px' }}>{i+1}</td>
                    <td style={{ padding: '8px', fontWeight: '600' }}>{disc.name}</td>
                    <td style={{ padding: '8px', textAlign: 'center' }}>{r ? `${r.home_result} ${disc.unit}` : '—'}</td>
                    <td style={{ padding: '8px', textAlign: 'center' }}>{r ? `${r.away_result} ${disc.unit}` : '—'}</td>
                    <td style={{ padding: '8px', textAlign: 'center', fontWeight: '700' }}>
                      {r?.winner === 'home' ? homeTeam?.name : r?.winner === 'away' ? awayTeam?.name : r?.winner === 'draw' ? 'DRAW' : '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {/* Signatures */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '48px' }}>
            <div style={{ textAlign: 'center', borderTop: '1px solid #000', paddingTop: '8px', minWidth: '150px' }}>
              <div style={{ fontSize: '11px', color: '#666' }}>Judge 1 (Home)</div>
              <div style={{ fontSize: '12px', fontWeight: '600' }}>{match?.judge1_name || '—'}</div>
            </div>
            <div style={{ textAlign: 'center', borderTop: '1px solid #000', paddingTop: '8px', minWidth: '150px' }}>
              <div style={{ fontSize: '11px', color: '#666' }}>Judge 2 (Away)</div>
              <div style={{ fontSize: '12px', fontWeight: '600' }}>{match?.judge2_name || '—'}</div>
            </div>
            <div style={{ textAlign: 'center', borderTop: '1px solid #000', paddingTop: '8px', minWidth: '150px' }}>
              <div style={{ fontSize: '11px', color: '#666' }}>Organizer</div>
              <div style={{ fontSize: '12px' }}>&nbsp;</div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
