import { useState } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const gold = '#c9a84c';

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => { logout(); navigate('/login'); };

  const role = user?.role || '';
  const isOrganizer = role === 'WSM_ADMIN' || role === 'ORGANIZER';
  const isReferee = role === 'REFEREE' || role === 'WSM_ADMIN';
  const isAthlete = role === 'ATHLETE';
  const isJudge = role === 'JUDGE';
  const isCoach = role === 'COACH';
  const isTeam = role === 'TEAM';

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', show: true },
    { label: 'Referee', path: '/referee', show: isReferee },
    { label: 'Organizer', path: '/organizer/competitions', show: isOrganizer },
    { label: 'My Profile', path: '/organizer/profile', show: isOrganizer },
    { label: 'ASL', path: '/asl', show: isOrganizer },
    { label: 'My Profile', path: '/athlete/profile', show: isAthlete },
    { label: '🏆 Competitions', path: '/athlete/competitions', show: isAthlete },
    { label: 'My Profile', path: '/judge/profile', show: isJudge },
    { label: 'ASL Matches', path: '/asl/judge', show: isJudge },
    { label: 'My Profile', path: '/coach/profile', show: isCoach },
    { label: 'My Team', path: '/team/profile', show: isTeam },
  ].filter(i => i.show);

  const helpLinks = isOrganizer ? [
    { label: '📖 HELP', url: 'https://ranking.worldstrongman.org/organizer/help' },
    { label: '📖 ASL HELP', url: 'https://ranking.worldstrongman.org/asl/help' },
    { label: '📖 MATCH HELP', url: 'https://ranking.worldstrongman.org/asl/match-help' },
  ] : [];

  return (
    <div style={{ background: '#0a0a0a', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      <style>{`
        @media (max-width: 768px) {
          .wsm-nav-desktop { display: none !important; }
          .wsm-user-desktop { display: none !important; }
          .wsm-hamburger { display: flex !important; }
          .wsm-header { padding: 0 16px !important; }
          .wsm-content { padding: 16px !important; }
        }
        @media (min-width: 769px) {
          .wsm-hamburger { display: none !important; }
          .wsm-mobile-menu { display: none !important; }
        }
        @media (max-width: 768px) {
          .wsm-banner-wrap { flex-direction: column !important; }
          .wsm-banner-wrap img, .wsm-banner-wrap > div:first-child { width: 100% !important; max-width: 100% !important; }
        }
      `}</style>

      {/* Header */}
      <div className="wsm-header" style={{ background: '#111', borderBottom: '1px solid #1e1e1e', padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '60px', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }} onClick={() => { navigate('/dashboard'); setMenuOpen(false); }}>
            <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" alt="WSM" style={{ height: '32px' }} />
            <span style={{ color: gold, fontSize: '11px', fontWeight: '700', letterSpacing: '2px' }}>WSM PLATFORM</span>
          </div>
          {/* Desktop nav */}
          <nav className="wsm-nav-desktop" style={{ display: 'flex', gap: '4px' }}>
            {navItems.map(item => <NavItem key={item.path} label={item.label} path={item.path} current={location.pathname} navigate={navigate} />)}
            {helpLinks.map(h => <a key={h.url} href={h.url} target="_blank" style={{ padding: '8px 14px', color: '#555', fontSize: '11px', letterSpacing: '2px', textDecoration: 'none' }}>{h.label}</a>)}
          </nav>
        </div>

        {/* Desktop user */}
        <div className="wsm-user-desktop" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#555', fontSize: '11px', letterSpacing: '1px', textTransform: 'uppercase', border: '1px solid #2a2a2a', padding: '3px 8px', borderRadius: '2px' }}>{role || 'user'}</span>
          <span style={{ color: '#444', fontSize: '13px' }}>{user?.email}</span>
          <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid #2a2a2a', color: '#666', padding: '6px 14px', borderRadius: '3px', cursor: 'pointer', fontSize: '12px' }}>Logout</button>
        </div>

        {/* Hamburger */}
        <button className="wsm-hamburger" onClick={() => setMenuOpen(!menuOpen)}
          style={{ display: 'none', flexDirection: 'column', gap: '5px', background: 'transparent', border: 'none', cursor: 'pointer', padding: '8px' }}>
          <span style={{ display: 'block', width: '22px', height: '2px', background: menuOpen ? gold : '#888', transition: 'all 0.2s', transform: menuOpen ? 'rotate(45deg) translate(5px, 5px)' : 'none' }} />
          <span style={{ display: 'block', width: '22px', height: '2px', background: menuOpen ? 'transparent' : '#888', transition: 'all 0.2s' }} />
          <span style={{ display: 'block', width: '22px', height: '2px', background: menuOpen ? gold : '#888', transition: 'all 0.2s', transform: menuOpen ? 'rotate(-45deg) translate(5px, -5px)' : 'none' }} />
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="wsm-mobile-menu" style={{ background: '#111', borderBottom: '1px solid #1e1e1e', padding: '8px 16px 16px', position: 'sticky', top: '60px', zIndex: 99 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            {navItems.map(item => {
              const active = item.path === '/dashboard' ? location.pathname === item.path : location.pathname.startsWith(item.path);
              return (
                <button key={item.path} onClick={() => { navigate(item.path); setMenuOpen(false); }}
                  style={{ background: active ? 'rgba(201,168,76,0.1)' : 'transparent', border: 'none', color: active ? gold : '#888', padding: '12px 14px', borderRadius: '3px', cursor: 'pointer', fontSize: '14px', fontWeight: active ? '700' : '400', textAlign: 'left' }}>
                  {item.label}
                </button>
              );
            })}
            {helpLinks.map(h => (
              <a key={h.url} href={h.url} target="_blank" onClick={() => setMenuOpen(false)}
                style={{ padding: '12px 14px', color: '#555', fontSize: '13px', textDecoration: 'none', display: 'block' }}>{h.label}</a>
            ))}
            <div style={{ borderTop: '1px solid #1e1e1e', marginTop: '8px', paddingTop: '8px' }}>
              <div style={{ color: '#444', fontSize: '12px', padding: '4px 14px' }}>{user?.email}</div>
              <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid #2a2a2a', color: '#666', padding: '8px 14px', borderRadius: '3px', cursor: 'pointer', fontSize: '12px', marginTop: '8px', width: '100%' }}>Logout</button>
            </div>
          </div>
        </div>
      )}

      <div className="wsm-content" style={{ padding: '32px' }}>
        {children}
      </div>
    </div>
  );
}

function NavItem({ label, path, current, navigate }) {
  const active = path === '/dashboard' ? current === path : current.startsWith(path);
  return (
    <button onClick={() => navigate(path)}
      style={{ background: active ? 'rgba(201,168,76,0.1)' : 'transparent', border: 'none', color: active ? gold : '#555', padding: '6px 14px', borderRadius: '3px', cursor: 'pointer', fontSize: '13px', fontWeight: active ? '600' : '400' }}>
      {label}
    </button>
  );
}
