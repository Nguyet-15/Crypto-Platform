import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from app.api.v1.health import get_database_check
from app.core.config import Settings
from app.core.errors import unexpected_error, validation_error
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_readiness_success(client):
    app.dependency_overrides[get_database_check] = lambda: lambda: None
    response = client.get("/api/v1/health/ready")
    assert response.json() == {"status": "ready", "database": "ok"}
    assert response.headers["x-request-id"]


def test_readiness_failure_is_sanitized(client):
    def unavailable():
        raise OperationalError("secret connection string", {}, Exception("secret"))

    app.dependency_overrides[get_database_check] = lambda: unavailable
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "database_unavailable"
    assert "secret" not in response.text


def test_modules_are_explicitly_unimplemented(client):
    response = client.get("/api/v1/modules")
    assert response.status_code == 200
    modules = response.json()
    assert len(modules) == 8
    assert {m["status"] for m in modules} == {"not_implemented"}


def test_not_found_and_cors(client):
    response = client.get("/missing", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 404
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert (
        "access-control-allow-origin"
        not in client.get(
            "/api/v1/health", headers={"Origin": "https://untrusted.invalid"}
        ).headers
    )


def test_settings_environment_override(tmp_path, monkeypatch):
    from pathlib import Path

    monkeypatch.chdir(tmp_path)
    assert all(Path(p).is_absolute() for p in Settings.model_config["env_file"])
    monkeypatch.setenv("DB_CONNECT_TIMEOUT", "7")
    assert Settings(_env_file=None).db_connect_timeout == 7


def test_settings_reject_invalid_timeout():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, db_connect_timeout=0)


def test_cors_preflight(client):
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_unexpected_error_is_sanitized():
    isolated = FastAPI()
    isolated.add_exception_handler(Exception, unexpected_error)

    @isolated.get("/fail")
    def fail():
        raise RuntimeError("secret")

    response = TestClient(isolated, raise_server_exceptions=False).get("/fail")
    assert response.status_code == 500
    assert "secret" not in response.text


def test_validation_error_does_not_echo_input():
    isolated = FastAPI()
    isolated.add_exception_handler(RequestValidationError, validation_error)

    @isolated.get("/items")
    def items(limit: int):
        return {"limit": limit}

    response = TestClient(isolated).get("/items?limit=secret")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "secret" not in response.text
