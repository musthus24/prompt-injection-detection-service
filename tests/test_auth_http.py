from app.security.jwt import create_access_token


def test_scan_requires_auth(client):
    request = client.post("/v1/scan", json={"prompt": "hello"})
    assert request.status_code == 401


def test_scan_with_valid_token_succeeds(client):
    token = create_access_token("test-client")
    request = client.post(
        "/v1/scan",
        json={"prompt": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert request.status_code == 200

