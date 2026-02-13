from __future__ import annotations

from typing import Any

import httpx

from app.providers.market.base import MarketDataProvider


class BinanceMarketDataProvider(MarketDataProvider):
    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def search_symbols(self, query: str) -> list[str]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/v3/exchangeInfo")
            response.raise_for_status()
            data = response.json()
        symbols = [s["symbol"] for s in data.get("symbols", [])]
        if not query:
            return symbols[:100]
        q = query.upper()
        return [s for s in symbols if q in s][:100]

    async def get_ohlcv(self, symbol: str, interval: str, limit: int) -> list[dict[str, Any]]:
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/v3/klines", params=params)
            response.raise_for_status()
            rows = response.json()
        out: list[dict[str, Any]] = []
        for r in rows:
            out.append({
                "open_time": r[0],
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "volume": float(r[5]),
                "close_time": r[6],
            })
        return out
