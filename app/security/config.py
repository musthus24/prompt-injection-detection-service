import os

JWT_SECRET = os.getenv("JWT_SECRET")

if JWT_SECRET is None:
    raise RuntimeError("JWT_SECRET is not set")