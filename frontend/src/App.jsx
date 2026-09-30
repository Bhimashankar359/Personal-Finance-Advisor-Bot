import { useEffect, useRef, useState } from "react";
const API = import.meta.env.VITE_API_URL || "http://localhost:5000";
const CHIPS = ["summary", "How can I save more money?", "Where am I spending too much?", "Create a budget for this month", "Analyze my spending", "How do I build an emergency fund?"];
const HELP = "Commands:\n• income 50000 salary\n• expense 250 food lunch\n• budget food 5000\n• goal Laptop 60000\n• save Laptop 2000\n• summary\nOr just ask me anything about your money.";
const inr = (n) => "₹" + Math.round(n || 0).toLocaleString("en-IN");

async function api(path, token, opts = {}) {
  const r = await fetch(API + path, { ...opts, headers: { "Content-Type": "application/json", ...(token && { Authorization: "Bearer " + token }) } });
  const j = r.status === 204 ? {} : await r.json().catch(() => ({}));
  if (!r.ok) throw Object.assign(new Error(j.error || "Request failed"), { status: r.status });
  return j;
}

function Login({ onAuth }) {
  const [mode, setMode] = useState("login"), [f, setF] = useState({ name: "", email: "", password: "" }), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr("");
    try { const j = await api(`/api/auth/${mode}`, null, { method: "POST", body: JSON.stringify(f) }); onAuth(j.token); }
    catch (x) { setErr(x.message === "Failed to fetch" ? "Cannot reach the server." : x.message); } setBusy(false);
  };
  return (
    <div className="login"><div className="card">
      <div className="avatar big">🤖</div><h1>Finance Advisor Bot</h1><p>Sign in to chat with your money assistant.</p>
      <a className="btn google" href={API + "/api/auth/google"}>Continue with Google</a><div className="or">or</div>
      <form onSubmit={submit}>
        {mode === "register" && <input placeholder="Name" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />}
        <input type="email" required placeholder="Email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} />
        <input type="password" required minLength={8} placeholder="Password (8+ chars)" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} />
        {err && <div className="err">{err}</div>}
        <button className="btn" disabled={busy}>{busy ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}</button>
      </form>
      <button className="link" onClick={() => setMode(mode === "login" ? "register" : "login")}>{mode === "login" ? "New here? Register" : "Have an account? Log in"}</button>
    </div></div>
  );
}

function Chat({ token, onLogout }) {
  const [msgs, setMsgs] = useState([{ from: "bot", text: "Hi! I'm your finance advisor bot. 👋\n\n" + HELP }]);
  const [input, setInput] = useState(""), [busy, setBusy] = useState(false), [sum, setSum] = useState(null), [user, setUser] = useState(null), end = useRef();
  const refresh = () => api("/api/dashboard/summary", token).then(setSum).catch(() => {});
  useEffect(() => { api("/api/auth/me", token).then(setUser).catch((e) => e.status === 401 && onLogout()); refresh(); }, []);
  useEffect(() => end.current?.scrollIntoView({ behavior: "smooth" }), [msgs, busy]);
  const send = async (text) => {
    text = text.trim(); if (!text || busy) return; setInput(""); setBusy(true); setMsgs((m) => [...m, { from: "me", text }]);
    try { const j = await api("/api/bot/message", token, { method: "POST", body: JSON.stringify({ text }) }); setMsgs((m) => [...m, { from: "bot", text: j.reply }]); refresh(); }
    catch (e) { if (e.status === 401) return onLogout(); setMsgs((m) => [...m, { from: "bot", text: "⚠️ " + e.message, error: true }]); }
    setBusy(false);
  };
  return (
    <div className="app">
      <aside>
        <h3>Snapshot</h3>
        {sum ? <>
          <div className="stat"><span>Income</span><b>{inr(sum.total_income)}</b></div>
          <div className="stat"><span>Expenses</span><b>{inr(sum.total_expenses)}</b></div>
          <div className="stat"><span>Savings</span><b>{inr(sum.savings)}</b></div>
          <div className="stat"><span>Savings rate</span><b>{sum.savings_rate_pct}%</b></div>
          <h3>Budgets</h3>{sum.budgets.length === 0 && <small>None yet. Try “budget food 5000”.</small>}
          {sum.budgets.map((b, i) => <div key={i}><small>{b.category}: {inr(b.spent)} / {inr(b.limit)}{b.spent > b.limit && " ⚠️ over"}</small>
            <div className="bar"><i className={b.spent > b.limit ? "over" : ""} style={{ width: Math.min(100, (b.spent / b.limit) * 100) + "%" }} /></div></div>)}
          <h3>Goals</h3>{sum.goals.length === 0 && <small>None yet. Try “goal Laptop 60000”.</small>}
          {sum.goals.map((g) => <div key={g.id}><small>{g.name}: {inr(g.current_amount)} / {inr(g.target_amount)}</small>
            <div className="bar"><i style={{ width: Math.min(100, (g.current_amount / g.target_amount) * 100) + "%" }} /></div></div>)}
        </> : <small>Loading…</small>}
      </aside>
      <main>
        <header><div className="avatar">🤖</div><div><b>Finance Advisor Bot</b><small>{busy ? "typing…" : "online"}</small></div>
          <span className="sp" />{user?.profile_picture && <img className="pic" src={user.profile_picture} alt="" referrerPolicy="no-referrer" />}
          <small>{user?.name}</small><button className="link" onClick={() => api("/api/auth/logout", token, { method: "POST" }).finally(onLogout)}>Logout</button></header>
        <div className="log">
          {msgs.map((m, i) => <div key={i} className={"row " + m.from}>{m.from === "bot" && <div className="avatar sm">🤖</div>}<div className={"bubble" + (m.error ? " error" : "")}>{m.text}</div></div>)}
          {busy && <div className="row bot"><div className="avatar sm">🤖</div><div className="bubble dots"><i /><i /><i /></div></div>}
          <div ref={end} />
        </div>
        <div className="chips">{CHIPS.map((c) => <button key={c} onClick={() => send(c)}>{c}</button>)}<button onClick={() => setMsgs((m) => [...m, { from: "bot", text: HELP }])}>help</button></div>
        <form className="composer" onSubmit={(e) => { e.preventDefault(); send(input); }}>
          <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type a command or ask a question…" maxLength={500} /><button className="btn" disabled={busy}>Send</button>
        </form>
        <small className="disc">AI replies are informational, not financial advice.</small>
      </main>
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  useEffect(() => { const t = new URLSearchParams(location.search).get("token"); if (t) { localStorage.setItem("token", t); setToken(t); history.replaceState({}, "", "/"); } }, []);
  const set = (t) => { t ? localStorage.setItem("token", t) : localStorage.removeItem("token"); setToken(t); };
  return token ? <Chat token={token} onLogout={() => set(null)} /> : <Login onAuth={set} />;
}
