from app.config.settings import deep_merge


def test_deep_merge():
    a = {"weights": {"price": 0.3, "tech": 0.4}}
    b = {"weights": {"tech": 0.8}}
    out = deep_merge(a, b)
    assert out["weights"]["price"] == 0.3
    assert out["weights"]["tech"] == 0.8
