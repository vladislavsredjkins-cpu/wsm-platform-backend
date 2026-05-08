import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = 'https://api.events.worldstrongman.org';
const teal = '#005B5C';
const bg = '#f7f4ef';

export default function VerifyEmail() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    axios.get(`${API}/participants/verify/${token}`)
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'));
  }, [token]);

  return (
    <div style={{ minHeight: '100vh', background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Roboto, sans-serif' }}>
      <div style={{ maxWidth: '480px', width: '100%', margin: '0 20px' }}>
        <div style={{ background: teal, padding: '24px', borderRadius: '8px 8px 0 0', textAlign: 'center' }}>
          <div style={{ color: '#E8D5B5', fontSize: '22px', fontWeight: '900', letterSpacing: '2px' }}>WSM EVENTS</div>
        </div>
        <div style={{ background: '#fff', padding: '40px 32px', borderRadius: '0 0 8px 8px', border: '1px solid #e8e0d0', borderTop: 'none', textAlign: 'center' }}>
          {status === 'loading' && (
            <>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
              <div style={{ color: '#888', fontSize: '16px' }}>Verifying your email...</div>
            </>
          )}
          {status === 'success' && (
            <>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
              <h2 style={{ color: '#1a1a1a', fontSize: '22px', margin: '0 0 12px' }}>Email Confirmed!</h2>
              <p style={{ color: '#555', fontSize: '14px', lineHeight: '1.6', margin: '0 0 24px' }}>
                Your registration is now pending organizer approval. You will receive an email once confirmed.
              </p>
              <button onClick={() => navigate('/tournaments')}
                style={{ padding: '12px 28px', background: teal, color: '#fff', border: 'none', borderRadius: '6px', fontSize: '14px', fontWeight: '700', cursor: 'pointer' }}>
                View Tournaments →
              </button>
            </>
          )}
          {status === 'error' && (
            <>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
              <h2 style={{ color: '#1a1a1a', fontSize: '22px', margin: '0 0 12px' }}>Invalid Link</h2>
              <p style={{ color: '#555', fontSize: '14px', lineHeight: '1.6' }}>
                This verification link is invalid or has already been used.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
