"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [configText, setConfigText] = useState("{}");
  const [message, setMessage] = useState("");

  const updateConfig = async () => {
    const payload = JSON.parse(configText);
    const res = await fetch(`${API_BASE}/config`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    setMessage(JSON.stringify(await res.json()));
  };

  const reset = async () => {
    const res = await fetch(`${API_BASE}/config/reset`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    setMessage(JSON.stringify(await res.json()));
  };

  return (
    <main style={{ padding: 24 }}>
      <h2>Admin</h2>
      <textarea value={token} onChange={(e) => setToken(e.target.value)} placeholder="Bearer token" />
      <textarea value={configText} onChange={(e) => setConfigText(e.target.value)} rows={15} cols={80} />
      <div>
        <button onClick={updateConfig}>Update config</button>
        <button onClick={reset}>Reset defaults</button>
      </div>
      <pre>{message}</pre>
    </main>
  );
}
