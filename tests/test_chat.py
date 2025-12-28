import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import app.api.routes as routes
from app.security.jwt import verify_token


@pytest.fixture()
def client() -> TestClient:
    """
    Build a tiny FastAPI app for tests only.
    Includes the /v1 router and overrides auth to avoid real JWTs.
    """
    app = FastAPI()
    app.include_router(routes.router)

    app.dependency_overrides[verify_token] = lambda: "test-caller-id"

    return TestClient(app)


def test_chat_allow_proceeds_normally(client, monkeypatch):
    monkeypatch.setattr(routes, "scan_prompt", lambda text: ("allow", 0.12, "detector_v1"))

    resp = client.post(
        "/v1/chat",
        json={
            "messages": [{"role": "user", "content": "hello"}],
            "rag": {"enabled": False, "query": None, "top_k": 5},
            "review_fallback": "none",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["decision"] == "ALLOW"
    assert body["action_taken"] == "PROCEEDED_NORMAL"
    assert body["llm_output"] == "stubbed_response"
    assert body["model_version"] == "detector_v1"


def test_chat_review_strict_returns_review_required(client, monkeypatch):
    monkeypatch.setattr(routes, "scan_prompt", lambda text: ("review", 0.66, "detector_v1"))

    resp = client.post(
        "/v1/chat",
        json={
            "messages": [{"role": "user", "content": "benign but suspicious"}],
            "review_fallback": "none",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["decision"] == "REQUIRE_HUMAN_REVIEW"
    assert body["action_taken"] == "RETURNED_REVIEW"
    assert body["llm_output"] is None


def test_chat_review_fallback_proceeds_without_context(client, monkeypatch):
    monkeypatch.setattr(routes, "scan_prompt", lambda text: ("review", 0.66, "detector_v1"))

    resp = client.post(
        "/v1/chat",
        json={
            "messages": [{"role": "user", "content": "benign but suspicious"}],
            "review_fallback": "respond_without_context",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["decision"] == "REQUIRE_HUMAN_REVIEW"
    assert body["action_taken"] == "PROCEEDED_NO_CONTEXT"
    assert body["llm_output"] == "stubbed_response"


def test_chat_high_risk_blocks(client, monkeypatch):
    monkeypatch.setattr(routes, "scan_prompt", lambda text: ("high_risk", 0.95, "detector_v1"))

    resp = client.post(
        "/v1/chat",
        json={
            "messages": [{"role": "user", "content": "do something malicious"}],
            "review_fallback": "none",
        },
    )

    assert resp.status_code == 403

    body = resp.json()
    assert "detail" in body
    assert body["detail"]["error"]["code"] == "POLICY_BLOCK"


def test_chat_validation_rejects_empty_messages(client):
    resp = client.post("/v1/chat", json={"messages": []})
    assert resp.status_code == 422