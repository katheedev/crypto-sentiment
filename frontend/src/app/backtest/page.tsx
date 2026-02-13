"use client";

import { useState } from "react";

import { backtest } from "@/lib/api";

export default function BacktestPage() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [interval, setInterval] = useState("1h");
  const [result, setResult] = useState<any | null>(null);

  return (
    <main style={{ padding: 24 }}>
      <h2>Backtest</h2>
      <input value={symbol} onChange={(e) => setSymbol(e.target.value)} />
      <input value={interval} onChange={(e) => setInterval(e.target.value)} />
      <button onClick={async () => setResult(await backtest(symbol, interval))}>Run backtest</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </main>
  );
}
