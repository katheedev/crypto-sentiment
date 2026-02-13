import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 24 }}>
      <h1>sentiment-crypto-lab</h1>
      <ul>
        <li><Link href="/dashboard">Dashboard</Link></li>
        <li><Link href="/backtest">Backtest</Link></li>
        <li><Link href="/admin">Admin</Link></li>
      </ul>
    </main>
  );
}
