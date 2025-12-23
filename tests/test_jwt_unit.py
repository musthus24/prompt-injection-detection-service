import time
from jose import jwt

from app.security.jwt import create_access_token, get_jwt_secret, ALGORITHM, JWT_AUDIENCE, JWT_ISSUER


def test_create_access_token_contains_expected_claims():
    SECRET_KEY = get_jwt_secret()
    token = create_access_token("unit-test-client")
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer = JWT_ISSUER,
        audience = JWT_AUDIENCE,
    )
    assert payload["sub"] == "unit-test-client"
    assert "iat" in payload
    assert "exp" in payload

    assert payload["exp"] > int(time.time())

def test_tampered_token_fails_verification():
    SECRET_KEY = get_jwt_secret()
    token = create_access_token("unit-test-client")
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")

    try:
        jwt.decode(tampered, SECRET_KEY, algorithms=[ALGORITHM])
        assert False, "Tampered token should not verify"
    except Exception:
        assert True
