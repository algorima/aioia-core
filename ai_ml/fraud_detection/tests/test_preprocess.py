from ai_ml.fraud_detection.app.services.preprocess_text import extract_patterns, extract_risk_signals


def test_extract_patterns_urls():
    p = extract_patterns("check https://example.com and email a@b.com")
    assert "https://example.com" in p["urls"]
    assert "a@b.com" in p["emails"]


def test_extract_risk_signals():
    sigs = extract_risk_signals("선입금 부탁드려요 급처")
    types = {s[0] for s in sigs}
    assert "prepayment" in types
    assert "urgent_sale" in types
