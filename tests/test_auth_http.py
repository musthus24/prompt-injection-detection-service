import os
os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-prod")
from app.security.jwt import create_access_token

def test_scan_requires_auth(client_no_auth):
    response = client_no_auth.post("/v1/scan", json={"prompt": "hello"})
    assert response.status_code == 401


def test_scan_with_valid_token_succeeds(client_no_auth):
    token = create_access_token("test-client")
    response = client_no_auth.post(
        "/v1/scan",
        json={"prompt": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
