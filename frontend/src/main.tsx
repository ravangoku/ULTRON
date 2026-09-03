import { FormEvent, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const MODES = ["conversation", "command", "research", "coding", "vision", "system", "automation", "focus", "silent"] as const;
type Mode = (typeof MODES)[number];
type Message = { id: string; role: "user" | "assistant"; text: string };
type SystemStatus = { status: string; llm_provider: string; emergency_stop: boolean; registered_tools: string[] };

function websocketUrl(): string {
  const url = new URL(API_URL);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = "/ws/chat";
  return url.toString();
}

function App() {
  const [messages, setMessages] = useState<Message[]>([{ id: "welcome", role: "assistant", text: "ULTRON core online. I am ready to assist within your approved permissions." }]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<Mode>("conversation");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [connection, setConnection] = useState("CONNECTING");
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/system/status`)
      .then((response) => response.ok ? response.json() as Promise<SystemStatus> : Promise.reject())
      .then((data) => { setStatus(data); setConnection("NOMINAL"); })
      .catch(() => setConnection("OFFLINE"));
    return () => socketRef.current?.close();
  }, []);

  const append = (role: Message["role"], text: string) => setMessages((current) => [...current, { id: crypto.randomUUID(), role, text }]);

  async function sendFallback(message: string) {
    try {
      const response = await fetch(`${API_URL}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message, mode }) });
      const body = await response.json();
      append("assistant", body.response ?? body.detail ?? "The command channel returned an invalid response.");
    } catch {
      append("assistant", "I cannot reach the local API. Start the ULTRON backend, then try again.");
      setConnection("OFFLINE");
    } finally { setBusy(false); }
  }

  function sendStream(message: string) {
    let response = "";
    const socket = new WebSocket(websocketUrl());
    socketRef.current = socket;
    const responseId = crypto.randomUUID();
    socket.onopen = () => socket.send(JSON.stringify({ message, mode }));
    socket.onmessage = ({ data }) => {
      const event = JSON.parse(data) as { type: string; value?: string; message?: string };
      if (event.type === "token") {
        response += event.value ?? "";
        setMessages((current) => {
          const last = current.at(-1);
          return last?.id === responseId ? [...current.slice(0, -1), { ...last, text: response }] : [...current, { id: responseId, role: "assistant", text: response }];
        });
      }
      if (event.type === "error") append("assistant", event.message ?? "Streaming failed.");
      if (event.type === "complete" || event.type === "error") { socket.close(); setBusy(false); }
    };
    socket.onerror = () => { socket.close(); sendFallback(message); };
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || busy) return;
    append("user", message); setInput(""); setBusy(true); sendStream(message);
  }

  return <main>
    <header>
      <div className="brand"><span className="mark">◈</span><span>ULTRON</span><small>PERSONAL AI OPERATING SYSTEM</small></div>
      <div className={`status ${connection.toLowerCase()}`}><span /> SYSTEM {connection}</div>
    </header>
    <section className="dashboard">
      <aside className="panel navigation"><p className="eyebrow">COMMAND MODE</p>{MODES.map((item) => <button className={mode === item ? "selected" : ""} onClick={() => setMode(item)} key={item}>{item}</button>)}<div className="emergency">✓ <span>Safety interlocks active</span></div></aside>
      <section className="center">
        <div className="core-wrap"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="core"><div className="core-inner">◈</div></div></div>
        <div className="wave" aria-label={busy ? "ULTRON is processing" : "ULTRON is waiting"}>{Array.from({ length: 36 }, (_, index) => <i key={index} style={{ height: `${12 + (index * 17) % 38}px` }} />)}</div>
        <p className="mode-label">{busy ? "PROCESSING REQUEST" : "AWAITING INPUT"}</p>
        <div className="conversation panel" aria-live="polite">{messages.map((message) => <article className={message.role} key={message.id}><label>{message.role === "assistant" ? "ULTRON" : "OPERATOR"}</label><p>{message.text}</p></article>)}</div>
        <form onSubmit={submit}><button type="button" className="mic" aria-label="Push-to-talk requires a configured voice provider">◉</button><input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Issue a directive..." aria-label="Message ULTRON" /><button className="send" aria-label="Send directive">→</button></form>
      </section>
      <aside className="right">
        <div className="panel metric"><p className="eyebrow">SYSTEM MATRIX</p><div><span>◌</span> Internet <b>{connection === "NOMINAL" ? "connected" : "unavailable"}</b></div><div><span>◌</span> Events <b>streaming</b></div><div><span>◌</span> Tools <b>{status?.registered_tools.length ?? 0} allowed</b></div></div>
        <div className="panel"><p className="eyebrow">ACTIVE PROTOCOL</p><h3>{mode.toUpperCase()}</h3><p>Consequential operations require a preview and explicit confirmation.</p></div>
        <div className="panel"><p className="eyebrow">VOICE PIPELINE</p><p>Push-to-talk is ready when an approved STT/TTS adapter is configured. The original voice profile never clones a performer.</p></div>
      </aside>
    </section>
  </main>;
}

createRoot(document.getElementById("root")!).render(<App />);
