import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const API = 'https://api.events.worldstrongman.org';
const accent = '#005B5C';
const bg = '#f7f4ef';
const sand = '#E8D5B5';

export default function JudgePage() {
  const { token } = useParams();
  const [session, setSession] = useState(null);
  const [competition, setCompetition] = useState(null);
  const [divisions, setDivisions] = useState([]);
  const [selectedDiv, setSelectedDiv] = useState(null);
  const [disciplines, setDisciplines] = useState([]);
  const [selectedDisc, setSelectedDisc] = useState(null);
  const [sheet, setSheet] = useState([]);
  const [inputs, setInputs] = useState({});
  const [saving, setSaving] = useState({});
  const [saved, setSaved] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/judges/access/${token}`)
      .then(res => {
        const { access_token, competition_id } = res.data;
        setSession({ access_token, competition_id });
        return axios.get(`${API}/competitions/${competition_id}`);
      })
      .then(res => {
        setCompetition(res.data);
        return axios.get(`${API}/divisions/${res.data.id}`);
      })
      .then(res => {
        setDivisions(res.data);
        setLoading(false);
      })
      .catch(() => {
        setError('Invalid or expired judge link.');
        setLoading(false);
      });
  }, [token]);

  useEffect(() => {
    if (!selectedDiv) return;
    axios.get(`${API}/divisions/${selectedDiv.id}/disciplines`)
      .then(res => {
        setDisciplines(res.data);
        setSelectedDisc(null);
        setSheet([]);
      });
  }, [selectedDiv]);

  useEffect(() => {
    if (!selectedDisc) return;
    axios.get(`${API}/results/discipline/${selectedDisc.id}`)
      .then(res => {
        setSheet(res.data);
        const init = {};
        res.data.forEach(p => {
          init[p.participant_id] = {
            primary_value: p.primary_value ?? "",
            reps: p.reps ?? "",
            status: p.status || "ok",
          };
        });
        setInputs(init);
        setSaved({});
      });
  }, [selectedDisc]);

  const authCfg = () => ({ headers: { Authorization: `Bearer ${session?.access_token}` } });

  const saveResult = async (participantId) => {
    setSaving(s => ({ ...s, [participantId]: true }));
    const val = inputs[participantId] || {};
    try {
      await axios.post(`${API}/results/discipline/${selectedDisc.id}`, {
        participant_id: participantId,
        primary_value: val.primary_value !== "" ? parseFloat(val.primary_value) : null,
        reps: val.reps !== "" ? parseInt(val.reps) : null,
        status: val.status || "ok",
      }, authCfg());
      setSaved(s => ({ ...s, [participantId]: true }));
      const res = await axios.get(`${API}/results/discipline/${selectedDisc.id}`);
      setSheet(res.data);
    } catch (e) {
      alert("Error saving result");
    } finally {
      setSaving(s => ({ ...s, [participantId]: false }));
    }
  };

  if (loading) return (
    <div style={{ minHeight: "100vh", background: bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ color: accent, fontSize: "16px" }}>Verifying access...</div>
    </div>
  );

  if (error) return (
    <div style={{ minHeight: "100vh", background: bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: "48px", marginBottom: "16px" }}>⚠️</div>
        <div style={{ color: "#1a1a1a", fontSize: "18px", marginBottom: "8px" }}>Access Denied</div>
        <div style={{ color: "#888", fontSize: "14px" }}>{error}</div>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: "100vh", background: bg, fontFamily: "Roboto, sans-serif" }}>
      <div style={{ background: accent, padding: "16px 24px", display: "flex", alignItems: "center", gap: "16px" }}>
        <div style={{ background: "#fff", color: accent, fontWeight: "900", fontSize: "18px", width: "36px", height: "36px", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "4px" }}>E</div>
        <div>
          <div style={{ color: "#fff", fontWeight: "700", fontSize: "16px" }}>{competition?.name}</div>
          <div style={{ color: "rgba(255,255,255,0.7)", fontSize: "12px" }}>Referee Panel</div>
        </div>
      </div>
      <div style={{ maxWidth: "900px", margin: "0 auto", padding: "24px 16px" }}>
        <div style={{ marginBottom: "24px" }}>
          <div style={{ color: "#888", fontSize: "11px", fontWeight: "700", letterSpacing: "1px", marginBottom: "10px" }}>SELECT DIVISION</div>
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {divisions.map(div => (
              <button key={div.id} onClick={() => setSelectedDiv(div)}
                style={{ padding: "8px 18px", borderRadius: "3px", border: `2px solid ${selectedDiv?.id === div.id ? accent : "#e8e0d0"}`, background: selectedDiv?.id === div.id ? accent : "#fff", color: selectedDiv?.id === div.id ? "#fff" : "#1a1a1a", fontWeight: "600", fontSize: "13px", cursor: "pointer" }}>
                {div.name}
              </button>
            ))}
          </div>
        </div>
        {selectedDiv && disciplines.length > 0 && (
          <div style={{ marginBottom: "24px" }}>
            <div style={{ color: "#888", fontSize: "11px", fontWeight: "700", letterSpacing: "1px", marginBottom: "10px" }}>SELECT DISCIPLINE</div>
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              {disciplines.map(disc => (
                <button key={disc.id} onClick={() => setSelectedDisc(disc)}
                  style={{ padding: "8px 18px", borderRadius: "3px", border: `2px solid ${selectedDisc?.id === disc.id ? accent : "#e8e0d0"}`, background: selectedDisc?.id === disc.id ? accent : "#fff", color: selectedDisc?.id === disc.id ? "#fff" : "#1a1a1a", fontWeight: "600", fontSize: "13px", cursor: "pointer" }}>
                  {disc.discipline_name}
                  <span style={{ marginLeft: "6px", fontSize: "10px", opacity: 0.7 }}>({disc.discipline_mode})</span>
                </button>
              ))}
            </div>
          </div>
        )}
        {selectedDisc && (
          <div>
            <div style={{ background: "#fff", border: "1px solid #e8e0d0", borderRadius: "4px", overflow: "hidden" }}>
              <div style={{ background: sand, padding: "12px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ fontWeight: "700", color: "#1a1a1a", fontSize: "15px", textTransform: "uppercase", letterSpacing: "1px" }}>{selectedDisc.discipline_name}</div>
                <div style={{ color: "#888", fontSize: "12px" }}>{selectedDisc.discipline_mode} · {sheet.length} athletes</div>
              </div>
              <div style={{ padding: "8px" }}>
                {sheet.map((p, idx) => {
                  const inp = inputs[p.participant_id] || { primary_value: "", reps: "", status: "ok" };
                  const isSaving = saving[p.participant_id];
                  const isSaved = saved[p.participant_id];
                  const unit = selectedDisc.discipline_mode === "max_reps" ? "Reps" :
                    selectedDisc.discipline_mode === "fastest_time" ? "Sec" :
                    selectedDisc.discipline_mode === "max_distance" ? "m" :
                    selectedDisc.discipline_mode === "static_hold" ? "Sec" :
                    selectedDisc.discipline_mode === "win_loss" ? "—" : "kg";
                  const valField = selectedDisc.discipline_mode === "max_reps" ? "reps" : "primary_value";
                  return (
                    <div key={p.participant_id} style={{ background: isSaved ? "#f0faf0" : "#fff", border: `1px solid ${isSaved ? "#c8e6c9" : "#e8e0d0"}`, borderRadius: "6px", padding: "16px", marginBottom: "10px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "14px" }}>
                        <div style={{ background: accent, color: "#fff", fontWeight: "900", fontSize: "20px", width: "44px", height: "44px", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "4px", flexShrink: 0 }}>{p.bib_no || "?"}</div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: "700", color: "#1a1a1a", fontSize: "16px" }}>{p.first_name} {p.last_name}</div>
                          <div style={{ color: "#888", fontSize: "12px" }}>{p.country} · Start #{p.start_position || idx + 1}</div>
                        </div>
                        {isSaved && <div style={{ color: "#4caf50", fontSize: "22px" }}>✓</div>}
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: "10px", alignItems: "end" }}>
                        <div>
                          <div style={{ color: "#888", fontSize: "11px", fontWeight: "700", letterSpacing: "1px", marginBottom: "6px" }}>RESULT ({unit})</div>
                          <input type="number" placeholder={unit}
                            value={inp[valField]}
                            onChange={e => setInputs(prev => ({ ...prev, [p.participant_id]: { ...prev[p.participant_id], [valField]: e.target.value } }))}
                            style={{ width: "100%", padding: "12px", border: "1px solid #e8e0d0", borderRadius: "4px", fontSize: "18px", fontWeight: "700", textAlign: "center" }}
                          />
                        </div>
                        <div>
                          <div style={{ color: "#888", fontSize: "11px", fontWeight: "700", letterSpacing: "1px", marginBottom: "6px" }}>STATUS</div>
                          <select value={inp.status}
                            onChange={e => setInputs(prev => ({ ...prev, [p.participant_id]: { ...prev[p.participant_id], status: e.target.value } }))}
                            style={{ width: "100%", padding: "12px", border: "1px solid #e8e0d0", borderRadius: "4px", fontSize: "14px" }}>
                            <option value="ok">OK</option>
                            <option value="dnf">DNF</option>
                            <option value="dns">DNS</option>
                          </select>
                        </div>
                        <button onClick={() => saveResult(p.participant_id)} disabled={isSaving}
                          style={{ background: isSaved ? "#4caf50" : accent, color: "#fff", border: "none", padding: "12px 20px", borderRadius: "4px", fontWeight: "700", fontSize: "14px", cursor: "pointer", whiteSpace: "nowrap" }}>
                          {isSaving ? "..." : isSaved ? "✓ SAVED" : "SAVE"}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
