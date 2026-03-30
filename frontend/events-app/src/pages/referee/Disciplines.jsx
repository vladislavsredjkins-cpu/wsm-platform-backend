import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import api from '../../api';

const gold = '#c9a84c';

export default function RefereeDisciplines() {
  const { divisionId } = useParams();
  const navigate = useNavigate();
  const [disciplines, setDisciplines] = useState([]);
  const [division, setDivision] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get(`/competition-divisions/${divisionId}`),
      api.get(`/competition-divisions/${divisionId}/disciplines`),
    ]).then(([divRes, discRes]) => {
      setDivision(divRes.data);
      setDisciplines(discRes.data);
    }).finally(() => setLoading(false));
  }, [divisionId]);

  return (
    <Layout>
      <div style={{ marginBottom: '24px', display: 'flex', gap: '8px', color: '#555', fontSize: '13px' }}>
        <button onClick={() => navigate('/referee')} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer', padding: 0 }}>Competitions</button>
        <span>›</span>
        <span style={{ color: '#888' }}>{division?.division_key} {division?.age_group}</span>
      </div>

      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ color: '#fff', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>
          {division?.division_key} {division?.age_group}
        </h1>
        <p style={{ color: '#555', fontSize: '13px', margin: 0 }}>Select discipline to enter results</p>
      </div>

      {loading && <p style={{ color: '#555' }}>Loading...</p>}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {disciplines.map((disc, i) => (
          <div
            key={disc.id}
            onClick={() => navigate(`/referee/${disc.id}/results`)}
            style={{ background: '#111', border: '1px solid #1e1e1e', borderRadius: '4px', padding: '18px 24px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
            onMouseEnter={e => e.currentTarget.style.borderColor = gold}
            onMouseLeave={e => e.currentTarget.style.borderColor = '#1e1e1e'}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ color: gold, fontWeight: '700', fontSize: '18px', width: '28px' }}>{i + 1}</div>
              <div>
                <div style={{ color: '#fff', fontWeight: '600', fontSize: '15px' }}>{disc.discipline_name}</div>
                <div style={{ color: '#555', fontSize: '12px', marginTop: '2px' }}>
                  {disc.discipline_mode}
                  {disc.result_unit ? ` · ${disc.result_unit}` : ''}
                  {disc.time_cap_seconds ? ` · ${disc.time_cap_seconds}s cap` : ''}
                  {disc.is_final ? ' · FINAL' : ''}
                </div>
              </div>
            </div>
            <span style={{ color: '#333', fontSize: '18px' }}>→</span>
          </div>
        ))}
        {!loading && disciplines.length === 0 && (
          <p style={{ color: '#444', textAlign: 'center', padding: '40px' }}>No disciplines added yet</p>
        )}
      </div>
    </Layout>
  );
}
