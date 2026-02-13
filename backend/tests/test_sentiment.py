from app.sentiment.service import aggregate_sentiment, score_posts


def test_sentiment_aggregation():
    posts = [
        {"text": "bullish move", "created_at": "2024-01-01T00:00:00Z"},
        {"text": "very bad crash", "created_at": "2024-01-01T00:03:00Z"},
    ]
    scored = score_posts(posts)
    buckets = aggregate_sentiment(scored, interval_minutes=5)
    assert len(buckets) >= 1
