const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function fetchSymbols(query: string) {
  const res = await fetch(`${API_BASE}/symbols?query=${encodeURIComponent(query)}`);
  return res.json();
}

export async function analyze(symbol: string, interval: string, limit = 200) {
  const res = await fetch(`${API_BASE}/analyze?symbol=${symbol}&interval=${interval}&limit=${limit}`);
  return res.json();
}

export async function predict(symbol: string, interval: string) {
  const res = await fetch(`${API_BASE}/predict?symbol=${symbol}&interval=${interval}`);
  return res.json();
}

export async function backtest(symbol: string, interval: string, limit = 300) {
  const res = await fetch(`${API_BASE}/backtest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, interval, limit })
  });
  return res.json();
}
