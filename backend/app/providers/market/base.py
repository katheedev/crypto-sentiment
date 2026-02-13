from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MarketDataProvider(ABC):
    @abstractmethod
    async def search_symbols(self, query: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def get_ohlcv(self, symbol: str, interval: str, limit: int) -> list[dict[str, Any]]:
        raise NotImplementedError
