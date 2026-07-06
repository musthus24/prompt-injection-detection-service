from app.mcp.policy import map_tool_call_decision


def test_deterministic_violation_wins_over_scanner():
    decision, reason = map_tool_call_decision("path_escape", "high_risk")
    assert decision == "block"
    assert reason == "path_escape"


def test_no_violation_no_scanner_allows():
    decision, reason = map_tool_call_decision(None, None)
    assert decision == "allow"


def test_scanner_high_risk_blocks():
    decision, reason = map_tool_call_decision(None, "high_risk")
    assert decision == "block"
    assert reason == "prompt_injection"


def test_scanner_review_tier_reviews():
    decision, reason = map_tool_call_decision(None, "review")
    assert decision == "review"


def test_scanner_allow_tier_allows():
    decision, reason = map_tool_call_decision(None, "allow")
    assert decision == "allow"
