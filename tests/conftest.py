import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def _set_test_env(monkeypatch):
    # Required by app/security/jwt.py get_jwt_secret()
    monkeypatch.setenv("JWT_SECRET", "test-secret-do-not-use-in-prod")