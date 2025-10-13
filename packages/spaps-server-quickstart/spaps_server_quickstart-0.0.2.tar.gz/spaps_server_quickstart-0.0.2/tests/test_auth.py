from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from spaps_server_quickstart.auth import (
    AuthenticationError,
    SpapsAuthMiddleware,
    build_spaps_auth_service,
)
from spaps_server_quickstart.settings import BaseServiceSettings


class AuthSettings(BaseServiceSettings):
    spaps_api_key: str | None = "api-key"
    spaps_application_id: str | None = "app-id"


def test_build_spaps_auth_service_requires_keys() -> None:
    settings = BaseServiceSettings()
    with pytest.raises(ValueError):
        build_spaps_auth_service(settings)

    auth_settings = AuthSettings()
    service = build_spaps_auth_service(auth_settings)
    assert service  # instantiated without hitting network


class DummyAuthService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def authenticate(self, token: str) -> dict[str, str]:
        if token == "denied":
            raise AuthenticationError("Authentication failed")
        self.calls.append(token)
        return {"user_id": "user"}

    async def aclose(self) -> None:  # pragma: no cover - not invoked in test
        return None


def test_spaps_auth_middleware_enforces_headers() -> None:
    app = FastAPI()
    auth_service = DummyAuthService()

    app.add_middleware(SpapsAuthMiddleware, auth_service=auth_service, exempt_paths={"/open"})

    @app.get("/open")
    async def open_endpoint() -> dict[str, str]:  # pragma: no cover - executed via client
        return {"status": "ok"}

    @app.get("/secure")
    async def secure_endpoint(request: Request) -> dict[str, Any]:  # pragma: no cover - executed via client
        return {"user": getattr(request.state, "authenticated_user", None)}

    client = TestClient(app)

    assert client.get("/open").status_code == 200
    assert client.get("/secure").status_code == 401
    assert client.get("/secure", headers={"Authorization": "Basic foo"}).status_code == 401

    response = client.get("/secure", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert auth_service.calls == ["token"]

    denied = client.get("/secure", headers={"Authorization": "Bearer denied"})
    assert denied.status_code == 401
