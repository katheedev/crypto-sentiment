from __future__ import annotations

from abc import ABC, abstractmethod


class SocialProvider(ABC):
    @abstractmethod
    async def fetch_posts(self, keywords: list[str], limit: int) -> list[dict]:
        raise NotImplementedError
