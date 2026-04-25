import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

export default function JudgeAccess() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get(`/judges/access/${token}`)
      .then(res => {
        localStorage.setItem('token', res.data.access_token);
        localStorage.setItem('competition_id', res.data.competition_id);
        navigate('/referee');
      })
      .catch(() => setError('Invalid or expired judge link.'));
  }, [token]);

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0a', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {error ? (
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: '#c9a84c', fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <div style={{ color: '#fff', fontSize: '18px', marginBottom: '8px' }}>Access Denied</div>
          <div style={{ color: '#555', fontSize: '14px' }}>{error}</div>
        </div>
      ) : (
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: '#c9a84c', fontSize: '32px', marginBottom: '16px' }}>⏳</div>
          <div style={{ color: '#888', fontSize: '14px' }}>Verifying access...</div>
        </div>
      )}
    </div>
  );
}
