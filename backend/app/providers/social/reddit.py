from __future__ import annotations

import httpx

from app.providers.social.base import SocialProvider


class RedditProvider(SocialProvider):
    def __init__(self, client_id: str | None, client_secret: str | None, user_agent: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent

    async def fetch_posts(self, keywords: list[str], limit: int) -> list[dict]:
        if not self.client_id or not self.client_secret:
            return []
        query = " OR ".join(keywords)
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": self.user_agent}) as client:
            token_response = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
            )
            token_response.raise_for_status()
            token = token_response.json().get("access_token")
            headers = {"Authorization": f"bearer {token}", "User-Agent": self.user_agent}
            search_response = await client.get(
                "https://oauth.reddit.com/r/all/search",
                params={"q": query, "limit": limit, "sort": "new", "restrict_sr": False},
                headers=headers,
            )
            search_response.raise_for_status()
            children = search_response.json().get("data", {}).get("children", [])
        return [{"text": c.get("data", {}).get("title", ""), "created_at": c.get("data", {}).get("created_utc")} for c in children]
