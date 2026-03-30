import { useState } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const teal = '#005B5C';
const sand = '#E8D5B5';

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const handleLogout = () => { logout(); navigate('/'); };
  const role = user?.role || '';
  const isOrganizer = role === 'WSM_ADMIN' || role.includes('ORGANIZER');
  const isReferee = role === 'REFEREE' || role === 'WSM_ADMIN' || role.includes('REFEREE');
  const isAthlete = role === 'ATHLETE';
  const isTeam = role === 'TEAM';

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', show: true },
    { label: 'Referee', path: '/referee', show: isReferee },
    { label: 'Competitions', path: '/organizer/competitions', show: isOrganizer },
    { label: 'My Profile', path: '/organizer/profile', show: isOrganizer },
    { label: 'My Profile', path: '/athlete/profile', show: isAthlete },
    { label: 'My Team', path: '/team/profile', show: isTeam },
  ].filter(i => i.show);

  return (
    <div style={{ background: '#f7f4ef', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      <style>{`
        .ev-nav-desktop { display: flex !important; }
        .ev-hamburger { display: none !important; }
        @media (max-width: 768px) {
          .ev-nav-desktop { display: none !important; }
          .ev-hamburger { display: flex !important; }
        }
      `}</style>

      {/* NAV */}
      <nav style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '0 24px', height: '60px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>
          <div style={{ width: '32px', height: '32px', background: teal, borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', fontWeight: '800', color: sand }}>E</div>
          <span style={{ fontSize: '14px', fontWeight: '700', color: '#1a1a1a' }}>WSM <span style={{ color: teal }}>Events</span></span>
        </div>

        <div className="ev-nav-desktop" style={{ gap: '4px', alignItems: 'center' }}>
          {navItems.map(item => {
            const active = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
            return (
              <button key={item.path} onClick={() => navigate(item.path)}
                style={{ background: active ? '#e8f4f0' : 'transparent', border: 'none', color: active ? teal : '#666', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: active ? '600' : '400' }}>
                {item.label}
              </button>
            );
          })}
        </div>

        <div className="ev-nav-desktop" style={{ gap: '12px', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: '#999', border: '1px solid #e8e0d0', padding: '3px 8px', borderRadius: '4px' }}>{role}</span>
          <span style={{ fontSize: '12px', color: '#888' }}>{user?.email}</span>
          <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid #e8e0d0', color: '#888', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>Logout</button>
        </div>

        <button className="ev-hamburger" onClick={() => setMenuOpen(!menuOpen)}
          style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: '8px', flexDirection: 'column', gap: '5px' }}>
          <span style={{ display: 'block', width: '22px', height: '2px', background: '#888' }}></span>
          <span style={{ display: 'block', width: '22px', height: '2px', background: '#888' }}></span>
          <span style={{ display: 'block', width: '22px', height: '2px', background: '#888' }}></span>
        </button>
      </nav>

      {/* MOBILE MENU */}
      {menuOpen && (
        <div style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '8px 16px 16px' }}>
          {navItems.map(item => (
            <button key={item.path} onClick={() => { navigate(item.path); setMenuOpen(false); }}
              style={{ display: 'block', width: '100%', background: 'transparent', border: 'none', color: '#1a1a1a', padding: '12px 0', fontSize: '14px', textAlign: 'left', cursor: 'pointer', borderBottom: '1px solid #f0ece4' }}>
              {item.label}
            </button>
          ))}
          <button onClick={handleLogout} style={{ display: 'block', width: '100%', background: 'transparent', border: 'none', color: '#888', padding: '12px 0', fontSize: '13px', textAlign: 'left', cursor: 'pointer', marginTop: '8px' }}>Logout</button>
        </div>
      )}

      {/* CONTENT */}
      <div style={{ padding: '32px 24px', maxWidth: '1100px', margin: '0 auto' }}>
        {children}
      </div>
    </div>
  );
}
