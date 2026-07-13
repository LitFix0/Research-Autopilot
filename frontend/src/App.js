import { useState, useEffect, useRef } from "react";

const API = "http://localhost:8000";

const COLORS = {
  bg: "#0a0a14", surface: "#111122", card: "#16162a",
  border: "#ffffff12", borderStrong: "#ffffff22",
  accent: "#6366f1", accentLight: "#818cf8", accentDim: "#6366f115", accentBorder: "#6366f130",
  text: "#e2e8f0", textMuted: "#94a3b8", textDim: "#64748b",
  success: "#10b981", successDim: "#10b98115",
  danger: "#ef4444", dangerDim: "#ef444415",
};

function OrbitalLogo({ size = 36 }) {
  const r = size / 2;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={r} cy={r} r={r * 0.88} fill="#6366f1" />
      <circle cx={r} cy={r} r={r * 0.68} fill="#4f46e5" />
      <ellipse cx={r} cy={r} rx={r * 0.88} ry={r * 0.34} fill="none" stroke="#a5b4fc" strokeWidth="1.5" />
      <ellipse cx={r} cy={r} rx={r * 0.88} ry={r * 0.34} fill="none" stroke="#a5b4fc" strokeWidth="1.5" transform={`rotate(60 ${r} ${r})`} />
      <ellipse cx={r} cy={r} rx={r * 0.88} ry={r * 0.34} fill="none" stroke="#a5b4fc" strokeWidth="1.5" transform={`rotate(120 ${r} ${r})`} />
      <circle cx={r} cy={r} r={r * 0.18} fill="#e0e7ff" />
      <circle cx={r * 1.88} cy={r} r={r * 0.1} fill="#c7d2fe" />
      <circle cx={r * 0.56} cy={r * 1.76} r={r * 0.1} fill="#c7d2fe" />
      <circle cx={r * 0.56} cy={r * 0.24} r={r * 0.1} fill="#c7d2fe" />
    </svg>
  );
}

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: "⬡" },
  { id: "new", label: "New research", icon: "+" },
  { id: "history", label: "Session history", icon: "≡" },
  { id: "reports", label: "Reports", icon: "⊞" },
];

function Sidebar({ active, onNav }) {
  return (
    <div style={{ width: 220, minHeight: "100vh", background: COLORS.surface, borderRight: `1px solid ${COLORS.border}`, display: "flex", flexDirection: "column", padding: "24px 0", flexShrink: 0 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "0 20px 28px" }}>
        <OrbitalLogo size={34} />
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.text }}>Research</div>
          <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.accentLight }}>Autopilot</div>
        </div>
      </div>
      <div style={{ fontSize: 10, color: COLORS.textDim, fontWeight: 600, letterSpacing: ".1em", padding: "0 20px 8px" }}>NAVIGATION</div>
      {NAV_ITEMS.map(item => (
        <button key={item.id} onClick={() => onNav(item.id)} style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 20px", background: active === item.id ? COLORS.accentDim : "transparent", border: "none", borderLeft: active === item.id ? `2px solid ${COLORS.accent}` : "2px solid transparent", color: active === item.id ? COLORS.text : COLORS.textMuted, fontSize: 13, cursor: "pointer", textAlign: "left", width: "100%", transition: "all 0.15s" }}>
          <span style={{ fontSize: 15, width: 18, textAlign: "center" }}>{item.icon}</span>
          {item.label}
        </button>
      ))}
      <div style={{ marginTop: "auto", padding: "20px", borderTop: `1px solid ${COLORS.border}` }}>
        <div style={{ fontSize: 11, color: COLORS.textDim, marginBottom: 4 }}>Powered by</div>
        <div style={{ fontSize: 11, color: COLORS.accentLight }}>Groq · CrewAI · Tavily</div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, sub, accent }) {
  return (
    <div style={{ background: accent ? COLORS.accentDim : COLORS.card, border: `1px solid ${accent ? COLORS.accentBorder : COLORS.border}`, borderRadius: 10, padding: "14px 16px" }}>
      <div style={{ fontSize: 11, color: accent ? COLORS.accentLight : COLORS.textDim, marginBottom: 6, letterSpacing: ".04em" }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 600, color: accent ? COLORS.accentLight : COLORS.text, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: COLORS.textDim, marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function Badge({ status }) {
  const map = {
    done: { bg: COLORS.successDim, color: COLORS.success, label: "done" },
    running: { bg: COLORS.accentDim, color: COLORS.accentLight, label: "running" },
    failed: { bg: COLORS.dangerDim, color: COLORS.danger, label: "failed" },
  };
  const s = map[status] || map.failed;
  return <span style={{ background: s.bg, color: s.color, fontSize: 11, padding: "2px 9px", borderRadius: 20, fontWeight: 500 }}>{s.label}</span>;
}

function PipelineBar({ stage }) {
  const steps = ["Planner", "Searcher ×3", "Synthesizer", "Critic"];
  const idx = steps.indexOf(stage);
  return (
    <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
      {steps.map((s, i) => (
        <div key={s} style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: i < idx ? COLORS.success : i === idx ? COLORS.accent : COLORS.border }} />
          {i < steps.length - 1 && <div style={{ width: 16, height: 1, background: i < idx ? COLORS.success : COLORS.border }} />}
        </div>
      ))}
    </div>
  );
}

function DeleteBtn({ onClick }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button onClick={onClick} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)} title="Remove session" style={{ background: hovered ? COLORS.dangerDim : "transparent", border: `1px solid ${hovered ? COLORS.danger : "transparent"}`, color: hovered ? COLORS.danger : COLORS.textDim, borderRadius: 6, padding: "3px 8px", cursor: "pointer", fontSize: 14, lineHeight: 1, transition: "all 0.15s" }}>×</button>
  );
}

function SessionsTable({ sessions, onDelete }) {
  return (
    <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 10, overflow: "hidden" }}>
      <div style={{ display: "grid", gridTemplateColumns: "36px 1fr 110px 70px 50px 60px 40px" }}>
        {["#", "Query", "Pipeline", "Status", "Time", "Date", ""].map((h, i) => (
          <div key={i} style={{ fontSize: 11, color: COLORS.textDim, padding: "10px 12px", background: COLORS.surface, borderBottom: `1px solid ${COLORS.border}`, letterSpacing: ".06em" }}>{h}</div>
        ))}
        {sessions.length === 0 && (
          <div style={{ gridColumn: "1 / -1", padding: "24px", textAlign: "center", fontSize: 13, color: COLORS.textDim }}>No sessions yet.</div>
        )}
        {sessions.map((s, i) => (
          <>
            <div key={`id-${s.id}`} style={{ fontSize: 12, color: COLORS.textDim, padding: "11px 12px", borderBottom: i < sessions.length - 1 ? `1px solid ${COLORS.border}` : "none", display: "flex", alignItems: "center" }}>{s.id}</div>
            <div key={`q-${s.id}`} style={{ fontSize: 12, color: COLORS.text, padding: "11px 12px", borderBottom: i < sessions.length - 1 ? `1px solid ${COLORS.border}` : "none", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", display: "flex", alignItems: "center" }}>{s.query}</div>
            <div key={`p-${s.id}`} style={{ padding: "11px 12px", borderBottom: i < sessions.length - 1 ? `1px solid ${COLORS.border}` : "none", display: "flex", alignItems: "center" }}><PipelineBar stage={s.stage || "Planner"} /></div>
            <div key={`s-${s.id}`} style={{ padding: "11px 12px", borderBottom: i < sessions.length - 1 ? `1px solid ${COLORS.border}` : "none", display: "flex", alignItems: "center" }}><Badge status={s.status} /></div>
            <div key={`t-${s.id}`} style={{ fontSize: 12, color: COLORS.textMuted, padding: "11px 12px", borderBottom: i < sessions.length - 1 ? `1px solid ${COLORS.border}` : "none", display: "flex", alignItems: "center" }}>{s.time || "—"}</div>
            <div key={`d-${s.id}`} style={{ fontSize: 12, color: COLORS.textDim, padding: "11px 12px", borderBottom: i < sessions.length - 1 ? `1px solid ${COLORS.border}` : "none", display: "flex", alignItems: "center" }}>{s.created_at ? s.created_at.slice(5, 10) : "—"}</div>
            <div key={`del-${s.id}`} style={{ padding: "11px 8px", borderBottom: i < sessions.length - 1 ? `1px solid ${COLORS.border}` : "none", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <DeleteBtn onClick={() => onDelete(s.id)} />
            </div>
          </>
        ))}
      </div>
    </div>
  );
}

// ── New Research with live pipeline progress ───────────
const STAGES = ["planner", "searchers", "synthesizer", "critic"];
const STAGE_LABELS = { planner: "Planner", searchers: "Searcher ×3", synthesizer: "Synthesizer", critic: "Critic" };

function NewResearch({ onComplete }) {
  const [query, setQuery] = useState("");
  const [running, setRunning] = useState(false);
  const [activeStage, setActiveStage] = useState(null);
  const [doneStages, setDoneStages] = useState([]);
  const [log, setLog] = useState([]);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const logRef = useRef(null);

  const appendLog = (msg) => setLog(prev => [...prev, msg]);

  const handleRun = async () => {
    if (!query.trim()) return;
    setRunning(true);
    setActiveStage(null);
    setDoneStages([]);
    setLog([]);
    setReport(null);
    setError(null);

    try {
      const res = await fetch(`${API}/api/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop();
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const evt = JSON.parse(line.slice(6));
          appendLog(evt.message);
          if (evt.type === "stage") {
            setActiveStage(evt.data?.stage);
            setDoneStages(prev => {
              const idx = STAGES.indexOf(evt.data?.stage);
              return STAGES.slice(0, idx);
            });
          }
          if (evt.type === "done") {
            setDoneStages(STAGES);
            setActiveStage(null);
            setReport(evt.data?.report_content);
            if (evt.data?.sessions) onComplete(evt.data.sessions);
          }
          if (evt.type === "error") setError(evt.message);
        }
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [log]);

  return (
    <div style={{ maxWidth: 640 }}>
      <div style={{ fontSize: 13, color: COLORS.textMuted, marginBottom: 16, lineHeight: 1.6 }}>
        Enter a research topic and the pipeline will break it into sub-questions, search the web, synthesize findings, and produce a markdown report.
      </div>

      <textarea value={query} onChange={e => setQuery(e.target.value)} placeholder="What do you want to research today?" rows={4} disabled={running}
        style={{ width: "100%", background: COLORS.card, border: `1px solid ${COLORS.borderStrong}`, borderRadius: 8, padding: "12px 14px", color: COLORS.text, fontSize: 14, resize: "vertical", fontFamily: "inherit", outline: "none", boxSizing: "border-box", opacity: running ? 0.6 : 1 }} />

      <div style={{ display: "flex", gap: 10, marginTop: 10 }}>
        <button onClick={handleRun} disabled={running || !query.trim()} style={{ flex: 1, padding: "10px 0", background: running ? COLORS.accentDim : COLORS.accent, color: running ? COLORS.accentLight : "#fff", border: `1px solid ${COLORS.accentBorder}`, borderRadius: 8, fontSize: 14, fontWeight: 500, cursor: running ? "not-allowed" : "pointer", transition: "all 0.2s" }}>
          {running ? "Running pipeline…" : "Run research pipeline"}
        </button>
        <button onClick={() => { setQuery(""); setLog([]); setReport(null); setError(null); setDoneStages([]); setActiveStage(null); }} disabled={running}
          style={{ padding: "10px 16px", background: "transparent", color: COLORS.textMuted, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 14, cursor: "pointer" }}>
          Clear
        </button>
      </div>

      {/* Pipeline stage tracker */}
      {(running || doneStages.length > 0) && (
        <div style={{ marginTop: 20, background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 8, padding: "14px 16px" }}>
          <div style={{ fontSize: 11, color: COLORS.textDim, marginBottom: 12, letterSpacing: ".06em" }}>PIPELINE PROGRESS</div>
          <div style={{ display: "flex", gap: 0 }}>
            {STAGES.map((stage, i) => {
              const isDone = doneStages.includes(stage);
              const isActive = activeStage === stage;
              return (
                <div key={stage} style={{ display: "flex", alignItems: "center", flex: 1 }}>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
                    <div style={{ width: 28, height: 28, borderRadius: "50%", background: isDone ? COLORS.success : isActive ? COLORS.accent : COLORS.border, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, transition: "all 0.3s", boxShadow: isActive ? `0 0 12px ${COLORS.accent}` : "none" }}>
                      {isDone ? "✓" : isActive ? "…" : i + 1}
                    </div>
                    <div style={{ fontSize: 10, color: isDone ? COLORS.success : isActive ? COLORS.accentLight : COLORS.textDim, textAlign: "center", whiteSpace: "nowrap" }}>{STAGE_LABELS[stage]}</div>
                  </div>
                  {i < STAGES.length - 1 && (
                    <div style={{ flex: 1, height: 2, background: isDone ? COLORS.success : COLORS.border, margin: "0 4px", marginBottom: 20, transition: "all 0.3s" }} />
                  )}
                </div>
              );
            })}
          </div>

          {/* Live log */}
          <div ref={logRef} style={{ marginTop: 14, background: COLORS.bg, borderRadius: 6, padding: "10px 12px", maxHeight: 100, overflowY: "auto", fontFamily: "monospace", fontSize: 11, color: COLORS.textMuted, lineHeight: 1.7 }}>
            {log.map((l, i) => <div key={i}>› {l}</div>)}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ marginTop: 16, background: COLORS.dangerDim, border: `1px solid ${COLORS.danger}`, borderRadius: 8, padding: "12px 14px", fontSize: 13, color: COLORS.danger }}>
          ❌ {error}
        </div>
      )}

      {/* Report preview */}
      {report && (
        <div style={{ marginTop: 16, background: COLORS.card, border: `1px solid ${COLORS.accentBorder}`, borderRadius: 8, padding: "14px 16px" }}>
          <div style={{ fontSize: 11, color: COLORS.accentLight, marginBottom: 10, letterSpacing: ".06em" }}>✅ REPORT GENERATED</div>
          <pre style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.7, whiteSpace: "pre-wrap", wordBreak: "break-word", maxHeight: 300, overflowY: "auto", margin: 0 }}>
            {report.slice(0, 1500)}{report.length > 1500 ? "\n\n…(truncated)" : ""}
          </pre>
        </div>
      )}

      {/* Static stage list when idle */}
      {!running && doneStages.length === 0 && (
        <div style={{ marginTop: 24 }}>
          <div style={{ fontSize: 11, color: COLORS.textDim, marginBottom: 10, letterSpacing: ".06em" }}>PIPELINE STAGES</div>
          {["Planner — breaks query into 3 sub-questions", "Searcher ×3 — parallel Tavily web search", "Synthesizer — merges findings into markdown", "Critic — validates and approves report"].map((s, i) => (
            <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 8 }}>
              <div style={{ width: 20, height: 20, borderRadius: "50%", background: COLORS.accentDim, border: `1px solid ${COLORS.accentBorder}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: COLORS.accentLight, flexShrink: 0 }}>{i + 1}</div>
              <div style={{ fontSize: 12, color: COLORS.textMuted, paddingTop: 2 }}>{s}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Reports({ sessions, onDelete }) {
  const done = sessions.filter(s => s.status === "done");
  const failed = sessions.filter(s => s.status !== "done");
  const [openReport, setOpenReport] = useState(null);
  const [loadingId, setLoadingId] = useState(null);

  const fetchReport = async (session) => {
    setLoadingId(session.id);
    try {
      const res = await fetch(`${API}/api/sessions/${session.id}/report`);
      const data = await res.json();
      setOpenReport(data);
    } catch {
      setOpenReport({ content: "Could not load report.", query: session.query });
    }
    setLoadingId(null);
  };

  if (openReport) return (
    <div>
      <button onClick={() => setOpenReport(null)} style={{ fontSize: 12, color: COLORS.accentLight, background: "transparent", border: `1px solid ${COLORS.accentBorder}`, borderRadius: 6, padding: "5px 12px", cursor: "pointer", marginBottom: 16 }}>← Back</button>
      <div style={{ fontSize: 15, fontWeight: 500, color: COLORS.text, marginBottom: 16 }}>{openReport.query}</div>
      <pre style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.8, whiteSpace: "pre-wrap", wordBreak: "break-word", background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 8, padding: "16px" }}>
        {openReport.content}
      </pre>
    </div>
  );

  return (
    <div>
      {done.length === 0 && <div style={{ fontSize: 13, color: COLORS.textDim, padding: "24px 0" }}>No approved reports yet. Run a research query first.</div>}
      {done.map(s => (
        <div key={s.id} style={{ background: COLORS.card, border: `1px solid ${COLORS.accentBorder}`, borderRadius: 10, padding: "16px 20px", marginBottom: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
            <div style={{ fontSize: 13, fontWeight: 500, color: COLORS.text }}>{s.query}</div>
            <Badge status={s.status} />
          </div>
          <div style={{ fontSize: 11, color: COLORS.textDim, marginBottom: 10 }}>Critic approved · {s.created_at?.slice(0, 10)}</div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => fetchReport(s)} disabled={loadingId === s.id} style={{ fontSize: 12, color: COLORS.accentLight, background: "transparent", border: `1px solid ${COLORS.accentBorder}`, borderRadius: 6, padding: "5px 12px", cursor: "pointer" }}>
              {loadingId === s.id ? "Loading…" : "Open report"}
            </button>
            <DeleteBtn onClick={() => onDelete(s.id)} />
          </div>
        </div>
      ))}
      {failed.length > 0 && (
        <>
          <div style={{ fontSize: 11, color: COLORS.textDim, letterSpacing: ".06em", margin: "16px 0 8px" }}>FAILED RUNS</div>
          {failed.map(s => (
            <div key={s.id} style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: "14px 20px", marginBottom: 8, opacity: 0.5, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 13, color: COLORS.textMuted }}>{s.query}</div>
                <div style={{ fontSize: 11, color: COLORS.textDim, marginTop: 4 }}>{s.created_at?.slice(0, 10)}</div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Badge status={s.status} />
                <DeleteBtn onClick={() => onDelete(s.id)} />
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

function Dashboard({ sessions, onDelete, onNav }) {
  const done = sessions.filter(s => s.status === "done").length;
  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 24 }}>
        <MetricCard label="TOTAL SESSIONS" value={sessions.length} sub="all time" />
        <MetricCard label="REPORTS SAVED" value={done} sub="in reports/" />
        <MetricCard label="AVG PIPELINE TIME" value="27s" sub="last session" accent />
        <MetricCard label="CRITIC APPROVED" value={done} sub={`of ${sessions.length} runs`} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
        <div style={{ fontSize: 11, color: COLORS.textDim, letterSpacing: ".06em" }}>RECENT SESSIONS</div>
        <button onClick={() => onNav("new")} style={{ fontSize: 12, color: COLORS.accentLight, background: COLORS.accentDim, border: `1px solid ${COLORS.accentBorder}`, borderRadius: 6, padding: "5px 12px", cursor: "pointer" }}>+ New research</button>
      </div>
      <SessionsTable sessions={sessions} onDelete={onDelete} />
    </div>
  );
}

function TopBar({ page }) {
  const titles = { dashboard: "Dashboard", new: "New research", history: "Session history", reports: "Reports" };
  return (
    <div style={{ height: 56, background: COLORS.surface, borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 24px", flexShrink: 0 }}>
      <div style={{ fontSize: 15, fontWeight: 500, color: COLORS.text }}>{titles[page]}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ fontSize: 11, color: COLORS.textDim }}>v1.0</div>
        <OrbitalLogo size={22} />
      </div>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [sessions, setSessions] = useState([]);

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API}/api/sessions`);
      const data = await res.json();
      setSessions(data);
    } catch { }
  };

  useEffect(() => { fetchSessions(); }, []);

  const handleDelete = async (id) => {
    try {
      await fetch(`${API}/api/sessions/${id}`, { method: "DELETE" });
      setSessions(prev => prev.filter(s => s.id !== id));
    } catch { }
  };

  const handleComplete = (newSessions) => {
    setSessions(newSessions);
    setTimeout(() => setPage("reports"), 1000);
  };

  const renderPage = () => {
    if (page === "dashboard") return <Dashboard sessions={sessions} onDelete={handleDelete} onNav={setPage} />;
    if (page === "new") return <NewResearch onComplete={handleComplete} />;
    if (page === "reports") return <Reports sessions={sessions} onDelete={handleDelete} />;
    if (page === "history") return <SessionsTable sessions={sessions} onDelete={handleDelete} />;
    return null;
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: COLORS.bg, fontFamily: "system-ui, sans-serif" }}>
      <Sidebar active={page} onNav={setPage} />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <TopBar page={page} />
        <div style={{ flex: 1, padding: 24, overflowY: "auto" }}>
          {renderPage()}
        </div>
      </div>
    </div>
  );
}