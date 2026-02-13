from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def generate_keywords(symbol: str, rules: dict[str, Any]) -> list[str]:
    base = symbol.replace("USDT", "")
    words = [symbol, base]
    extras = rules.get("extra_keywords", [])
    return list(dict.fromkeys([w for w in words + extras if w]))


def score_posts(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    analyzer = SentimentIntensityAnalyzer()
    scored = []
    for post in posts:
        text = post.get("text", "")
        compound = analyzer.polarity_scores(text)["compound"]
        scored.append({**post, "score": compound})
    return scored


def aggregate_sentiment(scored_posts: list[dict[str, Any]], interval_minutes: int) -> list[dict[str, Any]]:
    buckets: dict[int, list[float]] = defaultdict(list)
    interval_secs = interval_minutes * 60
    for post in scored_posts:
        ts = post.get("created_at")
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            epoch = int(dt.timestamp())
        else:
            epoch = int(ts or datetime.now(tz=timezone.utc).timestamp())
        bucket = epoch - (epoch % interval_secs)
        buckets[bucket].append(float(post["score"]))

    return [
        {"bucket": b, "sentiment": sum(vals) / len(vals), "count": len(vals)}
        for b, vals in sorted(buckets.items())
    ]
