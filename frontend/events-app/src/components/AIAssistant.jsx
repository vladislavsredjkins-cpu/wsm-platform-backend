import { useState, useRef, useEffect } from 'react';

const API_URL = 'https://api.events.worldstrongman.org/ai/chat';
const accent = '#005B5C';
const sand = '#E8D5B5';

export default function AIAssistant({ competition, divisions, disciplines, tab }) {
  const [open, setOpen] = useState(false);
  const storageKey = `wsm_ai_chat_${competitionId || 'general'}`;
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      return saved ? JSON.parse(saved) : [{ role: 'assistant', content: 'Hi! I am your WSM Events assistant. I can help you set up divisions, disciplines, judges, and more. What do you need help with?' }];
    } catch { return [{ role: 'assistant', content: 'Hi! I am your WSM Events assistant. I can help you set up divisions, disciplines, judges, and more. What do you need help with?' }]; }
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getContext = () => {
    const divList = divisions.map(d => `${d.name}`).join(', ') || 'none yet';
    const discList = disciplines.map(d => `${d.discipline_name} (${d.discipline_mode})`).join(', ') || 'none yet';
    return `
Competition: ${competition?.name || 'unnamed'} 
Date: ${competition?.date_start || 'not set'} 
City: ${competition?.city || 'not set'}, ${competition?.country || ''}
Sport: ${competition?.sport_type || 'strongman'}
Current tab: ${tab}
Divisions: ${divList}
Disciplines: ${discList}
`.trim();
  };

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: 'user', content: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'claude-sonnet-4-5',
          max_tokens: 1000,
          system: `You are a professional sports competition assistant for WSM Events platform — a world-class strongman and strength sports competition management system.

Current competition context:
${getContext()}

WSM OFFICIAL RULES (World Strongman International Union):

WEIGHT CATEGORIES:
Men: up to 70kg, 70.01-80kg, 80.01-95kg, 95.01-110kg, over 110kg
Women: up to 55kg, 55.01-65kg, 65.01-75kg, 75.01-85kg, over 85kg

AGE GROUPS:
Open (15+), Youths (15-18), Juniors (19-23), Veterans M1 (40-49), Veterans M2 (50-59), Veterans M3 (60-69), Veterans M4 (70+)

SCORING SYSTEM:
- Each athlete gets 1 attempt per discipline
- Points by place: 1st=N pts, 2nd=N-1 pts... last=1pt (N=number of athletes)
- Complete failure = 0 points
- Ties: points split equally; tiebreak by most 1st places, then most 2nd places
- Start order: random draw for discipline 1, then REVERSE order after each discipline (worst result goes first, leader goes last)
- Minimum 4 disciplines per official competition
- If >14 athletes in category: split into groups (stronger group competes last)

COMPETITION FORMATS:
1. Individual Events (Two Relays) - main format
2. Strongman Battles (2x2 teams) - 5 disciplines
3. Pro Division/Show - 5-7 disciplines chosen by organizer
4. Parastrongman - individual events
5. Ethnostrongman - individual events

STANDARD DISCIPLINES:
Relay #1 (Lift, time limit 180sec): Dumbbell, Log Lift, Axel Deadlift, Stone Over Bar
Relay #2 (Lift & Carry, time limit 180sec): Sandbag Carry, Farmers Walk, Yoke Race, Tire Flips

CLASSIC/PRO DISCIPLINES:
- Farmers Walk: 100-175kg, max 60m, 90sec limit, no straps
- Log Lift: from 110kg, 60sec limit (reps or weight)
- Super Yoke: up to 360kg, 30m, 90sec limit
- Deadlift: classical style, multiple variants (max weight/reps/hold)
- Shield Carry: 175-200kg, 50m, 90sec limit
- Atlas Stones: 110-180kg, 4-5 stones, 120sec limit
- Apollo-Axel: overhead, 120sec limit, up to 165kg
- Dumbbell Lift: 75-95kg, 90sec limit

STRONGMAN SCORING MODES:
- max_weight: athlete lifts maximum weight (Log Lift, Deadlift, Axle Press)
- max_reps: maximum repetitions (Car Deadlift, Viking Press)
- fastest_time: fastest time wins (Loading Race, Atlas Stones)
- max_distance: maximum distance (Farmer Walk, Yoke Walk)
- static_hold: longest hold time
- win_loss: head-to-head victory (Stick Pulling, Sumo)

STRONGMAN SCORING: judge inputs result → system ranks per discipline → points by rank (1st = N athletes, last = 1) → ties split points → TOTAL = sum → final PLACE. Reverse start order each discipline (leader starts last).

STICK PULLING RULES (WSF International):
Competition systems: Round Robin (mandatory if <6 athletes), Double Elimination (2 losses), Direct Elimination, Single Elimination
Match: best of 3 bouts (2 victories to win match). Score: 2:0 winner gets 2pts, 2:1 winner gets 2pts loser gets 1pt
Weight categories Men: 60/70/80/95/110/110+ kg
Weight categories Women: 55/65/75/85/85+ kg  
Age groups: Junior boys 12-13, Senior boys 14-15, Boys 16-17, Girls 16-17, Juniors 18-21, Men 18+, Women 18+, Veterans Men 40-49, Veterans Men 50+, Veterans Women 40+

STRONGMAN DISCIPLINES (standard):
Log Lift, Deadlift, Farmer Walk, Atlas Stones, Yoke Walk, Car Deadlift, Tire Flip, Loading Race, Overhead Press, Viking Press, Sandbag Carry, Keg Toss

DIVISION SETUP:
- Weight categories: organizer sets min/max kg (slider 40-200kg)
- Gender: Male / Female
- Age: Open / Junior (18-21) / Masters (40+)
- Format: Individual / Team

WSM EVENTS PRICING: €19 single event, €39 season pass (3 months)

Your role:
- Help organizers set up their competition correctly
- Give specific advice on divisions (weight categories, age groups, gender)  
- Recommend disciplines for strongman based on athlete count and level
- Advise on judging, start order, scoring
- Know stick pulling rules completely
- Be concise and practical — organizers are busy
- Respond in the same language the user writes in
- IMPORTANT: You are an ADVISOR only. You cannot create, modify or delete any data in the system. Never claim you created or modified anything. Always tell the user to do it themselves in the platform interface.`,
          messages: newMessages.map(m => ({ role: m.role, content: m.content }))
        })
      });
      const data = await res.json();
      const reply = data.content?.[0]?.text || 'Sorry, I could not process that.';
      setMessages(prev => {
        const updated = [...prev, { role: 'assistant', content: reply }];
        try { localStorage.setItem(storageKey, JSON.stringify(updated)); } catch {}
        return updated;
      });
    } catch(e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Кнопка открытия */}
      <button onClick={() => setOpen(!open)}
        style={{ position: 'fixed', bottom: '24px', right: '24px', width: '52px', height: '52px', borderRadius: '50%', background: accent, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 16px rgba(0,91,92,0.4)', zIndex: 1000, fontSize: '22px' }}>
        {open ? '✕' : '🤖'}
      </button>

      {/* Чат окно */}
      {open && (
        <div style={{ position: 'fixed', bottom: '88px', right: '24px', width: '360px', height: '500px', background: '#fff', border: '1px solid #e8e0d0', borderRadius: '12px', boxShadow: '0 8px 32px rgba(0,0,0,0.12)', display: 'flex', flexDirection: 'column', zIndex: 999 }}>
          {/* Header */}
          <div style={{ background: accent, padding: '14px 18px', borderRadius: '12px 12px 0 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ fontSize: '20px' }}>🤖</div>
            <div style={{ flex: 1 }}>
              <div style={{ color: '#fff', fontWeight: '700', fontSize: '14px' }}>WSM Assistant</div>
              <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '11px' }}>AI Competition Helper</div>
            </div>
            <button onClick={() => { const init = [{ role: 'assistant', content: 'Hi! I am your WSM Events assistant. How can I help?' }]; setMessages(init); try { localStorage.setItem(storageKey, JSON.stringify(init)); } catch {} }}
              style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.3)', color: 'rgba(255,255,255,0.7)', fontSize: '10px', padding: '3px 8px', borderRadius: '4px', cursor: 'pointer' }}>
              Clear
            </button>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {messages.map((m, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{
                  maxWidth: '80%', padding: '10px 14px', borderRadius: m.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                  background: m.role === 'user' ? accent : '#f7f4ef',
                  color: m.role === 'user' ? '#fff' : '#1a1a1a',
                  fontSize: '13px', lineHeight: '1.5'
                }}>
                  {m.content}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{ background: '#f7f4ef', padding: '10px 14px', borderRadius: '12px 12px 12px 2px', color: '#888', fontSize: '13px' }}>
                  Thinking...
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div style={{ padding: '12px', borderTop: '1px solid #e8e0d0', display: 'flex', gap: '8px' }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send()}
              placeholder='Ask about divisions, disciplines...'
              style={{ flex: 1, padding: '10px 12px', border: '1px solid #e8e0d0', borderRadius: '8px', fontSize: '13px', outline: 'none' }}
            />
            <button onClick={send} disabled={loading || !input.trim()}
              style={{ padding: '10px 16px', background: accent, color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', fontSize: '13px', cursor: 'pointer' }}>
              →
            </button>
          </div>
        </div>
      )}
    </>
  );
}
