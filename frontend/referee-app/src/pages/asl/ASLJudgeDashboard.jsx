import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';

export default function ASLJudgeDashboard() {
  const navigate = useNavigate();
  const [matches, setMatches] = useState([]);
  const [teams, setTeams] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/api/asl/matches/my'),
      api.get('/teams/'),
    ]).then(([mr, tr]) => {
      const teamMap = {};
      tr.data.forEach(t => { teamMap[t.id] = t; });
      setTeams(teamMap);
      const sorted = mr.data.sort((a, b) => {
        if (a.status === b.status) return 0;
        return a.status === 'scheduled' ? -1 : 1;
      });
      setMatches(sorted);
    }).finally(() => setLoading(false));
  }, []);

  const getTeamName = (id) => teams[id]?.name || '—';
  const scheduled = matches.filter(m => m.status === 'scheduled');
  const completed = matches.filter(m => m.status === 'completed');

  return (
    <Layout>
      <div style={{ marginBottom: '28px' }}>
        <div style={{ color: gold, fontSize: '11px', letterSpacing: '3px', marginBottom: '6px' }}>ASL LEAGUE</div>
        <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: 0 }}>My Matches</h1>
      </div>

      {loading && <div style={{ color: '#555', textAlign: 'center', padding: '40px' }}>Loading...</div>}

      {scheduled.length > 0 && (
        <div style={{ marginBottom: '32px' }}>
          <div style={{ color: '#888', fontSize: '10px', letterSpacing: '3px', marginBottom: '12px' }}>PENDING</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {scheduled.map(m => <MatchCard key={m.id} m={m} getTeamName={getTeamName} navigate={navigate} />)}
          </div>
        </div>
      )}

      {completed.length > 0 && (
        <div>
          <div style={{ color: '#888', fontSize: '10px', letterSpacing: '3px', marginBottom: '12px' }}>COMPLETED</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {completed.map(m => <MatchCard key={m.id} m={m} getTeamName={getTeamName} navigate={navigate} />)}
          </div>
        </div>
      )}

      {!loading && matches.length === 0 && (
        <div style={{ color: '#444', textAlign: 'center', padding: '60px 0', fontSize: '14px' }}>
          No matches assigned yet. Contact your organizer.
        </div>
      )}
    </Layout>
  );
}

function MatchCard({ m, getTeamName, navigate }) {
  const isCompleted = m.status === 'completed';
  return (
    <div style={{ background: '#111', border: `1px solid ${isCompleted ? '#1e1e1e' : '#2a2a1e'}`, borderRadius: '4px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ color: '#fff', fontWeight: '700', fontSize: '15px', minWidth: '140px', textAlign: 'right' }}>{getTeamName(m.home_team_id)}</div>
          <div style={{ background: '#1a1a1a', border: `1px solid ${isCompleted ? '#2a2a2a' : gold}`, borderRadius: '4px', padding: '4px 16px', color: isCompleted ? '#888' : gold, fontWeight: '900', fontSize: '18px', minWidth: '80px', textAlign: 'center' }}>
            {isCompleted ? `${m.home_score} : ${m.away_score}` : 'vs'}
          </div>
          <div style={{ color: '#fff', fontWeight: '700', fontSize: '15px', minWidth: '140px' }}>{getTeamName(m.away_team_id)}</div>
        </div>
        <div style={{ color: '#555', fontSize: '10px', letterSpacing: '2px', marginTop: '8px', paddingLeft: '156px' }}>
          R{m.round_number} · {isCompleted ? 'COMPLETED' : 'PENDING'}
        </div>
      </div>
      <button onClick={() => navigate(`/asl/matches/${m.id}`)}
        style={{ padding: '8px 20px', background: isCompleted ? 'transparent' : gold, color: isCompleted ? '#555' : '#000', border: isCompleted ? '1px solid #2a2a2a' : 'none', borderRadius: '3px', fontSize: '11px', fontWeight: '700', cursor: 'pointer', marginLeft: '20px' }}>
        {isCompleted ? 'VIEW' : 'PROTOCOL →'}
      </button>
    </div>
  );
}
