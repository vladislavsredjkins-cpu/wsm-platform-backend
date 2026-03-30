import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = 'https://ranking.worldstrongman.org';
const teal = '#005B5C';
const sand = '#E8D5B5';

export default function Landing() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ tournaments: 0, organizers: 0, athletes: 0 });
  const [installPrompt, setInstallPrompt] = React.useState(null);

  React.useEffect(() => {
    window.addEventListener('beforeinstallprompt', e => {
      e.preventDefault();
      setInstallPrompt(e);
    });
  }, []);

  const [showInstallGuide, setShowInstallGuide] = React.useState(false);
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);

  const handleInstall = async () => {
    if (installPrompt) {
      installPrompt.prompt();
      const result = await installPrompt.userChoice;
      if (result.outcome === 'accepted') setInstallPrompt(null);
    } else {
      setShowInstallGuide(true);
    }
  };
  const [competitions, setCompetitions] = useState([]);

  useEffect(() => {
    axios.get(`${API}/events-api/tournaments/all`).then(res => {
      const data = res.data || [];
      setCompetitions(data.slice(0, 6));
      const organizers = new Set(data.map(c => c.organizer_id)).size;
      setStats(s => ({ ...s, tournaments: data.length, organizers }));
    }).catch(() => {});
    axios.get(`${API}/athletes-list`).then(res => {
      setStats(s => ({ ...s, athletes: res.data?.length || 0 }));
    }).catch(() => {});
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: '#f7f4ef' }}>

      <nav style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '0 24px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" style={{ height: '36px' }} />
          <div>
            <div style={{ fontSize: '14px', fontWeight: '700', color: '#1a1a1a' }}>WSM <span style={{ color: teal }}>Events</span></div>
            <div style={{ fontSize: '10px', color: '#999' }}>by World Strongman</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button onClick={handleInstall} style={{ background: sand, border: 'none', color: '#7a5c2a', padding: '8px 18px', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>📲 Install App</button>
          <button onClick={() => navigate('/login')} style={{ background: 'transparent', border: `1px solid ${teal}`, color: teal, padding: '8px 18px', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>Sign in</button>
          <button onClick={() => navigate('/register')} style={{ background: teal, border: 'none', color: '#fff', padding: '8px 18px', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>Create event</button>
        </div>
      </nav>

      <div style={{ background: '#fff', borderBottom: '1px solid #e8e0d0', padding: '64px 24px 48px', textAlign: 'center' }}>
        <div style={{ maxWidth: '700px', margin: '0 auto' }}>
          <div style={{ display: 'inline-block', background: '#e8f4f0', color: teal, fontSize: '11px', fontWeight: '600', letterSpacing: '1.5px', padding: '4px 14px', borderRadius: '20px', marginBottom: '20px', textTransform: 'uppercase' }}>Competition tool</div>
          <h1 style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)', fontWeight: '800', color: '#1a1a1a', lineHeight: '1.15', marginBottom: '16px' }}>
            Run your strength sports<br /><span style={{ color: teal }}>tournament in minutes</span>
          </h1>
          <p style={{ fontSize: '16px', color: '#666', lineHeight: '1.7', marginBottom: '32px' }}>
            Digital tools for organizers — referee app, live results, protocols. Strongman, Strict Curl, Stick Pulling and more.
          </p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button onClick={() => navigate('/register')} style={{ background: teal, color: '#fff', border: 'none', padding: '14px 28px', borderRadius: '8px', fontSize: '15px', fontWeight: '700', cursor: 'pointer' }}>
              Create tournament <span style={{ background: sand, color: '#7a5c2a', fontSize: '12px', padding: '2px 8px', borderRadius: '10px', marginLeft: '8px' }}>from €19</span>
            </button>
            <button onClick={() => navigate('/login')} style={{ background: '#fff', color: teal, border: `1px solid ${teal}`, padding: '14px 28px', borderRadius: '8px', fontSize: '15px', fontWeight: '600', cursor: 'pointer' }}>
              Sign in
            </button>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '900px', margin: '48px auto 0', padding: '0 24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#1a1a1a', marginBottom: '8px', textAlign: 'center' }}>Choose your sport</h2>
        <p style={{ color: '#888', textAlign: 'center', marginBottom: '28px', fontSize: '14px' }}>One platform for all strength disciplines</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
          {[
            { name: 'Strongman', emoji: '🏋️', desc: 'Classic implements & events', live: true },
            { name: 'Strict Curl', emoji: '💪', desc: 'Barbell & dumbbell curls', live: true },
            { name: 'Stick Pulling', emoji: '🦯', desc: 'Traditional strength sport', live: true },
            { name: 'Powerlifting', emoji: '🏆', desc: 'Squat, bench, deadlift', live: false },
          ].map(s => (
            <div key={s.name} style={{ background: s.live ? '#fff' : '#f7f4ef', border: '1px solid #e8e0d0', borderTop: `3px solid ${s.live ? teal : '#ccc'}`, borderRadius: '10px', padding: '20px 16px', textAlign: 'center', opacity: s.live ? 1 : 0.6 }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>{s.emoji}</div>
              <div style={{ fontSize: '15px', fontWeight: '700', color: '#1a1a1a', marginBottom: '4px' }}>{s.name}</div>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '10px' }}>{s.desc}</div>
              <div style={{ display: 'inline-block', fontSize: '10px', fontWeight: '600', padding: '3px 10px', borderRadius: '10px', background: s.live ? '#e8f4f0' : '#f0f0f0', color: s.live ? teal : '#999' }}>
                {s.live ? '✓ AVAILABLE' : 'COMING SOON'}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ background: '#fff', borderTop: '1px solid #e8e0d0', borderBottom: '1px solid #e8e0d0', padding: '32px 24px', marginTop: '48px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', maxWidth: '600px', margin: '0 auto' }}>
          {[
            { value: stats.tournaments, label: 'Tournaments' },
            { value: stats.organizers, label: 'Organizers' },
            { value: stats.athletes, label: 'Athletes' },
          ].map((s, i) => (
            <div key={i} style={{ textAlign: 'center', padding: '0 24px', borderRight: i < 2 ? '1px solid #e8e0d0' : 'none', padding: '0 12px' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: '800', color: teal, lineHeight: '1' }}>{s.value}</div>
              <div style={{ fontSize: '12px', color: '#888', marginTop: '6px', letterSpacing: '0.5px', textTransform: 'uppercase' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {competitions.length > 0 && (
        <div style={{ maxWidth: '800px', margin: '48px auto', padding: '0 24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}><h2 style={{ fontSize: '20px', fontWeight: '700', color: '#1a1a1a', margin: 0 }}>Recent tournaments</h2><button onClick={() => navigate('/tournaments')} style={{ background: 'none', border: `1px solid ${teal}`, color: teal, padding: '6px 14px', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>View all →</button></div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px' }}>
            {competitions.map(c => (
              <div key={c.id} style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '10px', padding: '16px' }}>
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#1a1a1a', marginBottom: '4px' }}>{c.name}</div>
                <div style={{ fontSize: '12px', color: '#888' }}>{c.date_start || 'TBD'}{c.city ? ` · ${c.city}` : ''}{c.country ? ` · ${c.country}` : ''}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ maxWidth: '700px', margin: '48px auto', padding: '0 24px 64px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#1a1a1a', marginBottom: '8px', textAlign: 'center' }}>Simple pricing</h2>
        <p style={{ color: '#888', textAlign: 'center', marginBottom: '32px', fontSize: '14px' }}>No hidden fees. Pay per event or get a season pass.</p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div style={{ background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', padding: '28px' }}>
            <div style={{ fontSize: '13px', fontWeight: '600', color: '#888', marginBottom: '8px', textTransform: 'uppercase' }}>Event</div>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#1a1a1a', lineHeight: '1', marginBottom: '4px' }}>€19</div>
            <div style={{ fontSize: '13px', color: '#888', marginBottom: '20px' }}>per tournament</div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '24px' }}>
              {['1 tournament', 'Up to 50 athletes', 'Referee app', 'Protocols & PDF', 'Online registration'].map(f => (
                <li key={f} style={{ fontSize: '13px', color: '#555', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: teal, fontWeight: '700' }}>✓</span> {f}
                </li>
              ))}
            </ul>
            <button onClick={() => navigate('/register')} style={{ width: '100%', background: '#f7f4ef', border: `1px solid ${teal}`, color: teal, padding: '12px', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: 'pointer' }}>Get started</button>
          </div>
          <div style={{ background: teal, borderRadius: '12px', padding: '28px', position: 'relative' }}>
            <div style={{ position: 'absolute', top: '12px', right: '12px', background: sand, color: '#7a5c2a', fontSize: '11px', fontWeight: '700', padding: '3px 10px', borderRadius: '10px' }}>Popular</div>
            <div style={{ fontSize: '13px', fontWeight: '600', color: 'rgba(255,255,255,0.7)', marginBottom: '8px', textTransform: 'uppercase' }}>Season</div>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#fff', lineHeight: '1', marginBottom: '4px' }}>€39</div>
            <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)', marginBottom: '20px' }}>3 months unlimited</div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '24px' }}>
              {['Unlimited tournaments', 'Unlimited athletes', 'Referee app', 'Protocols & PDF', 'Priority support'].map(f => (
                <li key={f} style={{ fontSize: '13px', color: 'rgba(255,255,255,0.85)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: sand, fontWeight: '700' }}>✓</span> {f}
                </li>
              ))}
            </ul>
            <button onClick={() => navigate('/register')} style={{ width: '100%', background: '#fff', border: 'none', color: teal, padding: '12px', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: 'pointer' }}>Get started</button>
          </div>
        </div>
        <div style={{ marginTop: '24px', padding: '16px 20px', background: '#fff', border: '1px solid #e8e0d0', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ fontSize: '13px', color: '#888' }}>Want official WSM rankings and federation membership?</div>
          <a href="https://ranking.worldstrongman.org" style={{ fontSize: '13px', fontWeight: '600', color: teal, textDecoration: 'none' }}>ranking.worldstrongman.org →</a>
        </div>
      </div>

      <footer style={{ background: '#1a1a1a', color: '#888', padding: '24px', textAlign: 'center', fontSize: '12px' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>© 2026 World Strongman International Union. All rights reserved.</div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <a href="https://worldstrongman.org/privacy-policy" target="_blank" style={{ color: '#888', textDecoration: 'none' }}>Privacy Policy</a>
            <a href="https://worldstrongman.org/cookie-policy" target="_blank" style={{ color: '#888', textDecoration: 'none' }}>Cookie Policy</a>
            <a href="https://worldstrongman.org" target="_blank" style={{ color: teal, textDecoration: 'none' }}>worldstrongman.org</a>
          </div>
        </div>
      </footer>

      {showInstallGuide && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 2000, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', padding: '20px' }}>
          <div style={{ background: '#fff', borderRadius: '16px', padding: '28px', maxWidth: '400px', width: '100%' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#1a1a1a', marginBottom: '16px' }}>📲 Install WSM Events</h3>
            {isIOS ? (
              <div style={{ fontSize: '14px', color: '#555', lineHeight: '1.8' }}>
                <p style={{ marginBottom: '12px' }}>On iPhone/iPad:</p>
                <p>1. Tap the <strong>Share</strong> button (⬆️) at the bottom of Safari</p>
                <p>2. Scroll down and tap <strong>"Add to Home Screen"</strong></p>
                <p>3. Tap <strong>"Add"</strong> — done!</p>
              </div>
            ) : (
              <div style={{ fontSize: '14px', color: '#555', lineHeight: '1.8' }}>
                <p style={{ marginBottom: '12px' }}>On Android Chrome:</p>
                <p>1. Tap the <strong>⋮ menu</strong> (top right)</p>
                <p>2. Tap <strong>"Add to Home screen"</strong> or <strong>"Install app"</strong></p>
                <p>3. Tap <strong>"Add"</strong> — done!</p>
              </div>
            )}
            <button onClick={() => setShowInstallGuide(false)} style={{ width: '100%', marginTop: '20px', padding: '12px', background: teal, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700', cursor: 'pointer' }}>Got it</button>
          </div>
        </div>
      )}
      <CookieBanner />
    </div>
  );
}

function CookieBanner() {
  const [show, setShow] = React.useState(!localStorage.getItem('cookie_accepted'));
  if (!show) return null;
  return (
    <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#1a1a1a', color: '#fff', padding: '16px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', zIndex: 1000 }}>
      <p style={{ fontSize: '13px', color: '#ccc', margin: 0, flex: 1 }}>
        We use cookies to improve your experience. By using WSM Events you agree to our{' '}
        <a href="https://worldstrongman.org/privacy-policy" target="_blank" style={{ color: sand }}>Privacy Policy</a>.
      </p>
      <button onClick={() => { localStorage.setItem('cookie_accepted', '1'); setShow(false); }}
        style={{ background: teal, color: '#fff', border: 'none', padding: '8px 20px', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}>
        Accept
      </button>
    </div>
  );
}
