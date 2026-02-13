"use client";

import { useState } from "react";

import { ChartPanel } from "@/components/ChartPanel";
import { analyze, predict } from "@/lib/api";

export default function DashboardPage() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [interval, setInterval] = useState("1h");
  const [analysis, setAnalysis] = useState<any | null>(null);
  const [pred, setPred] = useState<any | null>(null);

  const run = async () => {
    const a = await analyze(symbol, interval);
    setAnalysis(a);
    const p = await predict(symbol, interval);
    setPred(p);
  };

  return (
    <main style={{ padding: 24 }}>
      <h2>Dashboard</h2>
      <input value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="Symbol" />
      <select value={interval} onChange={(e) => setInterval(e.target.value)}>
        {['1m', '5m', '15m', '1h', '4h', '1d'].map((v) => <option key={v}>{v}</option>)}
      </select>
      <button onClick={run}>Run analysis</button>
      {analysis && (
        <>
          <pre>{JSON.stringify(analysis.signals, null, 2)}</pre>
          <ChartPanel data={analysis.indicators} />
        </>
      )}
      {pred && <pre>{JSON.stringify(pred, null, 2)}</pre>}
    </main>
  );
}
