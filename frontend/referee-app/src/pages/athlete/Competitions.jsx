import { useState, useEffect } from 'react';
import { useAuth } from '../../AuthContext';
import Layout from '../../components/Layout';
import axios from 'axios';

const gold = '#c9a84c';
const API = 'https://ranking.worldstrongman.org';

export default function AthleteCompetitions() {
  const { user } = useAuth();
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [payingId, setPayingId] = useState(null);
  const [confirmedFee, setConfirmedFee] = useState({});
  const [couponCode, setCouponCode] = useState({});
  const [myRegistrations, setMyRegistrations] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    Promise.all([
      axios.get(`${API}/competitions/?published_only=true`),
      axios.get(`${API}/payments/entry-fee/my-registrations`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => ({ data: [] }))
    ]).then(([compsRes, regsRes]) => {
      setCompetitions(compsRes.data);
      setMyRegistrations(regsRes.data);
    }).finally(() => setLoading(false));
  }, []);

  const payStripe = async (comp) => {
    setPayingId(comp.id);
    try {
      const token = localStorage.getItem('token');
      // Create registration record
      await axios.post(`${API}/payments/entry-fee/register`, {
        competition_id: comp.id,
        athlete_email: user.email,
        amount_eur: comp.entry_fee,
        payment_method: 'stripe',
      }, { headers: { Authorization: `Bearer ${token}` } });
      // Redirect to Stripe
      const res = await axios.post(`${API}/payments/entry-fee/stripe`, {
        competition_id: comp.id,
        athlete_email: user.email,
        amount_eur: comp.entry_fee,
        payment_method: 'stripe',
        coupon_code: couponCode[comp.id] || null,
        success_url: `${window.location.origin}/athlete/competitions?paid=true&comp=${comp.id}`,
        cancel_url: `${window.location.origin}/athlete/competitions?cancelled=true`,
      }, { headers: { Authorization: `Bearer ${token}` } });
      window.location.href = res.data.checkout_url;
    } catch(e) {
      alert(e.response?.data?.detail || 'Payment error');
    } finally { setPayingId(null); }
  };

  const payCrypto = async (comp) => {
    setPayingId(comp.id);
    try {
      const token = localStorage.getItem('token');
      // Create registration record
      await axios.post(`${API}/payments/entry-fee/register`, {
        competition_id: comp.id,
        athlete_email: user.email,
        amount_eur: comp.entry_fee,
        payment_method: 'crypto',
      }, { headers: { Authorization: `Bearer ${token}` } });
      // Create crypto payment
      const amountUsd = Math.round(comp.entry_fee * 1.08 * 100) / 100;
      const res = await axios.post(`${API}/payments/entry-fee/crypto`, {
        competition_id: comp.id,
        athlete_email: user.email,
        amount_usd: amountUsd,
      }, { headers: { Authorization: `Bearer ${token}` } });

      const msg = `💰 CRYPTO PAYMENT\n\nSend exactly: ${res.data.pay_amount} USDT (TRC-20)\n\nTo address:\n${res.data.pay_address}\n\nPayment ID: ${res.data.payment_id}\n\nWSM Fee: $${res.data.wsm_fee}\nOrganizer: $${res.data.organizer_payout}\n\n⚠️ Non-refundable`;
      alert(msg);
    } catch(e) {
      alert(e.response?.data?.detail || 'Crypto payment error');
    } finally { setPayingId(null); }
  };

  if (loading) return <Layout><div style={{color:'#555',padding:'40px',textAlign:'center'}}>Loading...</div></Layout>;

  return (
    <Layout>
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '20px' }}>
        <div style={{ color: gold, fontSize: '10px', letterSpacing: '4px', marginBottom: '24px' }}>
          🏆 COMPETITIONS — REGISTER & PAY
        </div>

        {competitions.length === 0 && (
          <div style={{ color: '#444', textAlign: 'center', padding: '60px' }}>
            No competitions available
          </div>
        )}

        {competitions.map(comp => (
          <div key={comp.id} style={{
            background: '#0a0a0a',
            border: '1px solid #1a1a1a',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '16px'
          }}>
            {/* Competition Info */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ color: '#fff', fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>
                  {comp.name}
                </div>
                <div style={{ color: '#555', fontSize: '11px', letterSpacing: '1px' }}>
                  📍 {comp.city || '—'}, {comp.country || '—'} &nbsp;·&nbsp;
                  📅 {comp.date_start || '—'}
                  {comp.registration_deadline && (
                    <span style={{ color: '#c44c4c', marginLeft: '10px' }}>
                      ⏰ Deadline: {comp.registration_deadline}
                    </span>
                  )}
                </div>
              </div>
              <div style={{
                background: comp.competition_type === 'WORLD' ? '#1a1000' : '#0a1a0a',
                border: `1px solid ${comp.competition_type === 'WORLD' ? gold : '#1a3a1a'}`,
                borderRadius: '4px',
                padding: '4px 12px',
                fontSize: '10px',
                color: comp.competition_type === 'WORLD' ? gold : '#4cc44c',
                letterSpacing: '2px'
              }}>
                {comp.competition_type || 'OPEN'}
              </div>
            </div>

            {/* Registration status */}
            {myRegistrations.find(r => r.competition_id === comp.id && r.status === 'PAID') && (
              <div style={{ marginTop: '12px', padding: '10px 16px', background: '#0a1a0a', border: '1px solid #1a4a1a', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '16px' }}>✅</span>
                <span style={{ color: '#4cc44c', fontSize: '12px', fontWeight: '700', letterSpacing: '1px' }}>REGISTERED & PAID</span>
                <span style={{ color: '#555', fontSize: '10px', marginLeft: 'auto' }}>Entry fee confirmed</span>
              </div>
            )}
            {/* Entry Fee */}
            {comp.entry_fee_enabled && comp.entry_fee && !myRegistrations.find(r => r.competition_id === comp.id && r.status === 'PAID') && (
              <div style={{ marginTop: '16px', padding: '14px', background: '#0d1a0d', border: '1px solid #1a3a1a', borderRadius: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                  <div>
                    <div style={{ color: '#4cc44c', fontSize: '12px', letterSpacing: '2px', marginBottom: '4px' }}>
                      💰 ENTRY FEE: <span style={{ fontSize: '20px', fontWeight: '700', color: gold }}>€{comp.entry_fee}</span>
                    </div>
                    <div style={{ color: '#c44c4c', fontSize: '10px', letterSpacing: '1px' }}>
                      ⚠️ Non-refundable
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '200px' }}>
                    {/* Non-refundable checkbox */}
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={confirmedFee[comp.id] || false}
                        onChange={e => setConfirmedFee({...confirmedFee, [comp.id]: e.target.checked})}
                        style={{ width: '14px', height: '14px' }}
                      />
                      <span style={{ color: '#666', fontSize: '10px', letterSpacing: '0.5px' }}>
                        I understand the fee is non-refundable
                      </span>
                    </label>

                    {/* Coupon */}
                    {confirmedFee[comp.id] && (
                      <input
                        type="text"
                        placeholder="Coupon code (optional)"
                        value={couponCode[comp.id] || ''}
                        onChange={e => setCouponCode({...couponCode, [comp.id]: e.target.value})}
                        style={{ width: '100%', padding: '8px 12px', background: '#0a0a0a', border: '1px solid #2a2a2a', color: '#fff', borderRadius: '4px', fontSize: '12px', outline: 'none', marginBottom: '8px' }}
                      />
                    )}
                    {/* Payment buttons */}
                    {confirmedFee[comp.id] && (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          onClick={() => payStripe(comp)}
                          disabled={payingId === comp.id}
                          style={{
                            flex: 1, padding: '10px', background: gold, color: '#000',
                            border: 'none', borderRadius: '4px', fontSize: '11px',
                            fontWeight: '700', cursor: 'pointer', letterSpacing: '1px'
                          }}>
                          {payingId === comp.id ? '...' : '💳 PAY BY CARD'}
                        </button>
                        <button
                          onClick={() => payCrypto(comp)}
                          disabled={payingId === comp.id}
                          style={{
                            flex: 1, padding: '10px', background: '#0a1a2a',
                            color: '#4cc4c4', border: '1px solid #1a4a4a',
                            borderRadius: '4px', fontSize: '11px',
                            fontWeight: '700', cursor: 'pointer', letterSpacing: '1px'
                          }}>
                          {payingId === comp.id ? '...' : '₿ PAY USDT'}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Free competition */}
            {!comp.entry_fee_enabled && !myRegistrations.find(r => r.competition_id === comp.id && r.status === 'PAID') && (
              <div style={{ marginTop: '12px', color: '#4cc44c', fontSize: '11px', letterSpacing: '1px' }}>
                ✅ Free registration
              </div>
            )}
          </div>
        ))}
      </div>
    </Layout>
  );
}
