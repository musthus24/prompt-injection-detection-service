import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.main import app

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))



@pytest.fixture()
def client():
    app.dependency_overrides[routes.verify_token] = lambda: "test-caller-id"
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}


@pytest.fixture()
def client_no_auth():
    app.dependency_overrides = {}
    with TestClient(app) as c:
        yield c
