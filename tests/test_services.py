"""Tests para los servicios de Airtable y Slack en modo dry-run."""

from __future__ import annotations

import pytest

from app.models import LeadForm


@pytest.fixture(autouse=True)
def _force_dry_run(monkeypatch: pytest.MonkeyPatch):
    """Fuerza modo dry-run para todos los tests de servicios."""
    monkeypatch.setenv("DRY_RUN", "true")

    from app.config import Settings
    import app.config as config_module

    config_module.settings = Settings()


@pytest.fixture()
def sample_lead() -> LeadForm:
    return LeadForm(
        nombre="Test User",
        email="test@ejemplo.com",
        mensaje="Mensaje de prueba.",
    )


# ── Airtable ────────────────────────────────────────────────────────

class TestAirtableService:
    """Tests del servicio de Airtable en modo dry-run."""

    @pytest.mark.asyncio
    async def test_dry_run_returns_fake_id(self, sample_lead: LeadForm):
        from app.services.airtable import create_record

        result = await create_record(sample_lead)
        assert "id" in result
        assert result["id"].startswith("rec_dry_")

    @pytest.mark.asyncio
    async def test_dry_run_returns_fields(self, sample_lead: LeadForm):
        from app.services.airtable import create_record

        result = await create_record(sample_lead)
        fields = result["fields"]
        assert fields["Nombre"] == "Test User"
        assert fields["Email"] == "test@ejemplo.com"
        assert fields["Mensaje"] == "Mensaje de prueba."
        assert "Fecha" in fields


# ── Slack ────────────────────────────────────────────────────────────

class TestSlackService:
    """Tests del servicio de Slack en modo dry-run."""

    @pytest.mark.asyncio
    async def test_dry_run_returns_true(self, sample_lead: LeadForm):
        from app.services.slack import send_notification

        result = await send_notification(sample_lead, "rec_fake_123")
        assert result is True

    @pytest.mark.asyncio
    async def test_build_message_structure(self, sample_lead: LeadForm):
        from app.services.slack import _build_message

        payload = _build_message(sample_lead, "rec_abc")
        assert "blocks" in payload
        blocks = payload["blocks"]
        # Header, sección con fields, sección con mensaje, contexto, divider
        assert len(blocks) == 5
        assert blocks[0]["type"] == "header"
