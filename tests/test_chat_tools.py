import app.api.routes as routes


def test_chat_tool_executes_on_allow(client, monkeypatch):
    monkeypatch.setattr(routes, "scan_prompt", lambda _prompt: ("allow", 0.01, "test-model"))

    payload = {
        "messages": [{"role": "user", "content": "hello"}],
        "tool_request": {"name": "web_search", "args": {"query": "roblox", "top_k": 2}},
    }

    res = client.post("/v1/chat", json=payload)
    assert res.status_code == 200

    body = res.json()
    assert body["decision"] == "ALLOW"
    assert body["action_taken"] == "PROCEEDED_NORMAL"

    assert body["tool_result"]["name"] == "web_search"
    assert body["tool_result"]["executed"] is True
    assert "output" in body["tool_result"]
    assert "results" in body["tool_result"]["output"]


def test_chat_tool_denied_on_review_proceeded_no_context(client, monkeypatch):
    monkeypatch.setattr(routes, "scan_prompt", lambda _prompt: ("review", 0.50, "test-model"))

    payload = {
        "messages": [{"role": "user", "content": "suspicious-ish"}],
        "review_fallback": "respond_without_context",
        "tool_request": {"name": "web_search", "args": {"query": "roblox"}},
    }

    res = client.post("/v1/chat", json=payload)
    assert res.status_code == 200

    body = res.json()
    assert body["decision"] == "REQUIRE_HUMAN_REVIEW"
    assert body["action_taken"] == "PROCEEDED_NO_CONTEXT"

    assert body["tool_result"]["name"] == "web_search"
    assert body["tool_result"]["executed"] is False
    assert body["tool_result"]["reason"] == "policy_denied"


def test_chat_block_short_circuits_tool_validation(client, monkeypatch):
    monkeypatch.setattr(routes, "scan_prompt", lambda _prompt: ("high_risk", 0.99, "test-model"))

    payload = {
        "messages": [{"role": "user", "content": "definitely bad"}],
        "tool_request": {"name": "web_search", "args": {"query": "x", "unexpected": 123}},
    }

    res = client.post("/v1/chat", json=payload)
    assert res.status_code == 403

    body = res.json()
    assert body["detail"]["error"]["code"] == "POLICY_BLOCK"
