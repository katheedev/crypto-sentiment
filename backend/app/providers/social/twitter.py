from __future__ import annotations

import httpx

from app.providers.social.base import SocialProvider


class TwitterProvider(SocialProvider):
    def __init__(self, bearer_token: str | None) -> None:
        self.bearer_token = bearer_token

    async def fetch_posts(self, keywords: list[str], limit: int) -> list[dict]:
        if not self.bearer_token:
            return []
        query = " OR ".join(keywords)
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        params = {"query": query, "max_results": min(100, limit), "tweet.fields": "created_at,text"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://api.twitter.com/2/tweets/search/recent", params=params, headers=headers)
            response.raise_for_status()
            data = response.json().get("data", [])
        return [{"text": d.get("text", ""), "created_at": d.get("created_at")} for d in data]
