import { useAuth } from '../AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const gold = '#c9a84c';

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const role = user?.role || '';
  const isOrganizer = role === 'WSM_ADMIN' || role === 'ORGANIZER';
  const isReferee = role === 'REFEREE' || role === 'WSM_ADMIN';
  const isAthlete = role === 'ATHLETE';
  const isJudge = role === 'JUDGE';
  const isCoach = role === 'COACH';
  const isTeam = role === 'TEAM';

  return (
    <div style={{ background: '#0a0a0a', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ background: '#111', borderBottom: '1px solid #1e1e1e', padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '60px', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>
            <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" alt="WSM" style={{ height: '32px' }} />
            <span style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px' }}>WSM PLATFORM</span>
          </div>
          <nav style={{ display: 'flex', gap: '4px' }}>
            <NavItem label="Dashboard" path="/dashboard" current={location.pathname} navigate={navigate} />
            {isReferee && <NavItem label="Referee" path="/referee" current={location.pathname} navigate={navigate} />}
            {isOrganizer && <NavItem label="Organizer" path="/organizer/competitions" current={location.pathname} navigate={navigate} />}
            {isOrganizer && <NavItem label="ASL" path="/asl" current={location.pathname} navigate={navigate} />}
            {isOrganizer && <a href="https://ranking.worldstrongman.org/organizer/help" target="_blank" style={{ padding: '8px 14px', color: '#555', fontSize: '11px', letterSpacing: '2px', textDecoration: 'none' }}>📖 HELP</a>}
            {isOrganizer && <a href="https://ranking.worldstrongman.org/asl/help" target="_blank" style={{ padding: '8px 14px', color: '#555', fontSize: '11px', letterSpacing: '2px', textDecoration: 'none' }}>📖 ASL HELP</a>}
            {isOrganizer && <a href="https://ranking.worldstrongman.org/asl/match-help" target="_blank" style={{ padding: '8px 14px', color: '#555', fontSize: '11px', letterSpacing: '2px', textDecoration: 'none' }}>📖 MATCH HELP</a>}
            {isAthlete && <NavItem label="My Profile" path="/athlete/profile" current={location.pathname} navigate={navigate} />}
            {isJudge && <NavItem label="My Profile" path="/judge/profile" current={location.pathname} navigate={navigate} />}
            {isJudge && <NavItem label="ASL Matches" path="/asl/judge" current={location.pathname} navigate={navigate} />}
            {isCoach && <NavItem label="My Profile" path="/coach/profile" current={location.pathname} navigate={navigate} />}
            {isTeam && <NavItem label="My Team" path="/team/profile" current={location.pathname} navigate={navigate} />}
          </nav>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#555', fontSize: '11px', letterSpacing: '1px', textTransform: 'uppercase', border: '1px solid #2a2a2a', padding: '3px 8px', borderRadius: '2px' }}>
            {role || 'user'}
          </span>
          <span style={{ color: '#444', fontSize: '13px' }}>{user?.email}</span>
          <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid #2a2a2a', color: '#666', padding: '6px 14px', borderRadius: '3px', cursor: 'pointer', fontSize: '12px' }}>
            Logout
          </button>
        </div>
      </div>
      <div style={{ padding: '32px' }}>
        {children}
      </div>
    </div>
  );
}

function NavItem({ label, path, current, navigate }) {
  const active = path === '/dashboard' ? current === path : current.startsWith(path);
  return (
    <button
      onClick={() => navigate(path)}
      style={{
        background: active ? 'rgba(201,168,76,0.1)' : 'transparent',
        border: 'none',
        color: active ? gold : '#555',
        padding: '6px 14px',
        borderRadius: '3px',
        cursor: 'pointer',
        fontSize: '13px',
        fontWeight: active ? '600' : '400',
      }}
    >
      {label}
    </button>
  );
}
