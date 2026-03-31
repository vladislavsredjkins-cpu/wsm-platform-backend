import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { getCompetitions } from '../api';
import Layout from '../components/Layout';

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const role = user?.role || '';

  useEffect(() => {
    if (role === 'ATHLETE') navigate('/athlete/profile');
    else if (role === 'JUDGE') navigate('/judge/profile');
    else if (role === 'COACH') navigate('/coach/profile');
    else if (role === 'TEAM') navigate('/team/profile');
  }, [role]);

  if (['ATHLETE','JUDGE','COACH','TEAM'].includes(role)) return null;

  return <OrganizerDashboard />;
}

function OrganizerDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCompetitions(user?.organizer_id)
      .then(res => setCompetitions(res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ color: '#1a1a1a', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>Dashboard</h1>
        <p style={{ color: '#888', fontSize: '13px', margin: 0 }}>Welcome back, {user?.email}</p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px', marginBottom: '40px' }}>
        <StatCard label="Competitions" value={competitions.length} />
        <StatCard label="Active" value={competitions.filter(c => !c.date_end || new Date(c.date_end) >= new Date()).length} />
      </div>
      <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h2 style={{ color: '#1a1a1a', fontSize: '16px', fontWeight: '600', margin: 0 }}>Recent Competitions</h2>
        <button onClick={() => navigate('/organizer/competitions')} style={{ background: 'transparent', border: '1px solid #005B5C', color: '#005B5C', padding: '6px 16px', borderRadius: '3px', cursor: 'pointer', fontSize: '12px', fontWeight: '600' }}>
          + New Competition
        </button>
      </div>
      {loading && <p style={{ color: '#888' }}>Loading...</p>}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {competitions.slice(0, 5).map(c => (
          <div key={c.id}
            onClick={() => navigate(`/organizer/competitions/${c.id}`)}
            style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
            onMouseEnter={e => e.currentTarget.style.borderColor = '#005B5C'}
            onMouseLeave={e => e.currentTarget.style.borderColor = '#e8e0d0'}
          >
            <div>
              <div style={{ color: '#1a1a1a', fontWeight: '600', fontSize: '15px', marginBottom: '3px' }}>{c.name}</div>
              <div style={{ color: '#888', fontSize: '12px' }}>{c.date_start || 'No date'}{c.city ? ` · ${c.city}` : ''}{c.country ? ` · ${c.country}` : ''}</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ background: 'rgba(0,91,92,0.08)', color: '#005B5C', fontSize: '11px', fontWeight: '700', padding: '3px 8px', borderRadius: '2px' }}>Q {c.coefficient_q}</div>
              <span style={{ color: '#aaa' }}>→</span>
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}

function StatCard({ label, value }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '4px', padding: '20px 24px' }}>
      <div style={{ color: '#888', fontSize: '11px', fontWeight: '600', letterSpacing: '1px', marginBottom: '8px' }}>{label.toUpperCase()}</div>
      <div style={{ color: '#1a1a1a', fontSize: '28px', fontWeight: '700' }}>{value}</div>
    </div>
  );
}