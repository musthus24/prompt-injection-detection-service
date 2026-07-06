import app.mcp.middleware as middleware


def test_unknown_tool_blocked():
    decision, reason, args_obj = middleware.decide("delete_everything", {})
    assert decision == "block"
    assert reason == "unknown_tool"
    assert args_obj is None


def test_schema_invalid_blocked():
    decision, reason, args_obj = middleware.decide("read_file", {"path": 123})
    assert decision == "block"
    assert reason == "schema_invalid"
    assert args_obj is None


def test_read_file_path_escape_blocked():
    decision, reason, _ = middleware.decide("read_file", {"path": "../../etc/passwd"})
    assert decision == "block"
    assert reason == "path_escape"


def test_read_file_valid_allowed():
    decision, reason, _ = middleware.decide("read_file", {"path": "notes.txt"})
    assert decision == "allow"


def test_fetch_url_ssrf_blocked(monkeypatch):
    monkeypatch.setattr(middleware.ssrf, "check_url", lambda url: "ssrf_blocked")
    decision, reason, _ = middleware.decide("fetch_url", {"url": "http://169.254.169.254/"})
    assert decision == "block"
    assert reason == "ssrf_blocked"


def test_fetch_url_allowed(monkeypatch):
    monkeypatch.setattr(middleware.ssrf, "check_url", lambda url: None)
    decision, reason, _ = middleware.decide("fetch_url", {"url": "https://example.com"})
    assert decision == "allow"


def test_send_email_bad_recipient_blocked():
    decision, reason, _ = middleware.decide(
        "send_email", {"to": "attacker@evil.example", "body": "hello"}
    )
    assert decision == "block"
    assert reason == "recipient_not_allowed"


def test_send_email_scanner_never_run_when_recipient_blocked(monkeypatch):
    called = []
    monkeypatch.setattr(
        middleware,
        "scan_prompt",
        lambda body: called.append(body) or ("high_risk", 0.95, "test-model"),
    )
    middleware.decide("send_email", {"to": "attacker@evil.example", "body": "hello"})
    assert called == []  # first-block-wins: scanner must not run


def test_send_email_high_risk_body_blocked(monkeypatch):
    monkeypatch.setattr(middleware, "scan_prompt", lambda body: ("high_risk", 0.95, "test-model"))
    decision, reason, _ = middleware.decide(
        "send_email", {"to": "alerts@company.example", "body": "malicious"}
    )
    assert decision == "block"
    assert reason == "prompt_injection"


def test_send_email_review_body_held(monkeypatch):
    monkeypatch.setattr(middleware, "scan_prompt", lambda body: ("review", 0.6, "test-model"))
    decision, reason, _ = middleware.decide(
        "send_email", {"to": "alerts@company.example", "body": "suspicious"}
    )
    assert decision == "review"


def test_send_email_clean_body_allowed(monkeypatch):
    monkeypatch.setattr(middleware, "scan_prompt", lambda body: ("allow", 0.1, "test-model"))
    decision, reason, _ = middleware.decide(
        "send_email", {"to": "alerts@company.example", "body": "hello"}
    )
    assert decision == "allow"
