from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import os


def get_jwt_secret() -> str:
    SECRET_KEY = os.getenv("JWT_SECRET")
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET is not set")
    return SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_ISSUER = os.getenv("JWT_ISSUER", "prompt-injection-detection-service")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "prompt-injection-clients")


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    SECRET_KEY = get_jwt_secret()
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


security = HTTPBearer(auto_error=False)

def verify_token(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """
    Purpose: enforce that requests include a valid Bearer token.

    Returns:
      - the token subject (sub) if valid

    Raises:
      - 401 if missing/invalid/expired
    """
    SECRET_KEY = get_jwt_secret()

    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    token = creds.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer = JWT_ISSUER,
            audience = JWT_AUDIENCE,
        )
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing sub",
            )
        return subject
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
