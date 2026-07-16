"""Tests del endpoint FastAPI /leads en modo dry-run."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _force_dry_run(monkeypatch: pytest.MonkeyPatch):
    """Asegura que todos los tests corran en modo dry-run."""
    monkeypatch.setenv("DRY_RUN", "true")


@pytest.fixture()
def client() -> TestClient:
    """TestClient fresco (recarga config con env parcheado)."""
    # Re-importar para que Settings recoja el env parcheado
    from app.config import Settings

    import app.config as config_module

    config_module.settings = Settings()

    from app.main import app

    return TestClient(app)


VALID_LEAD = {
    "nombre": "Ana García",
    "email": "ana@ejemplo.com",
    "mensaje": "Necesito una automatización para mi negocio.",
}


class TestHealthEndpoint:
    """Tests para GET /health."""

    def test_health_returns_ok(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_health_shows_dry_run(self, client: TestClient):
        resp = client.get("/health")
        assert resp.json()["dry_run"] == "true"


class TestLeadEndpoint:
    """Tests para POST /leads."""

    def test_create_lead_success(self, client: TestClient):
        resp = client.post("/leads", json=VALID_LEAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "ok"
        assert data["lead_id"] is not None
        assert data["lead_id"].startswith("rec_dry_")

    def test_create_lead_returns_detail(self, client: TestClient):
        resp = client.post("/leads", json=VALID_LEAD)
        assert "Lead registrado" in resp.json()["detail"]

    def test_missing_field_returns_422(self, client: TestClient):
        resp = client.post("/leads", json={"nombre": "Ana"})
        assert resp.status_code == 422

    def test_invalid_email_returns_422(self, client: TestClient):
        bad = {**VALID_LEAD, "email": "no-valido"}
        resp = client.post("/leads", json=bad)
        assert resp.status_code == 422

    def test_empty_body_returns_422(self, client: TestClient):
        resp = client.post("/leads", json={})
        assert resp.status_code == 422
