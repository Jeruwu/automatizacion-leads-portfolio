"""Tests de validación para los modelos Pydantic."""

import pytest
from pydantic import ValidationError

from app.models import LeadForm, LeadResponse


# ── LeadForm: datos válidos ─────────────────────────────────────────

class TestLeadFormValid:
    """Casos exitosos de validación."""

    def test_valid_lead(self):
        lead = LeadForm(
            nombre="María López",
            email="maria@ejemplo.com",
            mensaje="Quiero más información.",
        )
        assert lead.nombre == "María López"
        assert lead.email == "maria@ejemplo.com"
        assert lead.mensaje == "Quiero más información."

    def test_minimal_fields(self):
        lead = LeadForm(nombre="A", email="a@b.co", mensaje="X")
        assert lead.nombre == "A"


# ── LeadForm: datos inválidos ───────────────────────────────────────

class TestLeadFormInvalid:
    """Casos que deben fallar la validación."""

    def test_missing_nombre(self):
        with pytest.raises(ValidationError):
            LeadForm(email="a@b.com", mensaje="Hola")  # type: ignore[call-arg]

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            LeadForm(nombre="Juan", mensaje="Hola")  # type: ignore[call-arg]

    def test_missing_mensaje(self):
        with pytest.raises(ValidationError):
            LeadForm(nombre="Juan", email="a@b.com")  # type: ignore[call-arg]

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LeadForm(nombre="Juan", email="no-es-email", mensaje="Hola")

    def test_nombre_too_long(self):
        with pytest.raises(ValidationError):
            LeadForm(
                nombre="A" * 121,
                email="a@b.com",
                mensaje="Hola",
            )

    def test_mensaje_empty_string(self):
        with pytest.raises(ValidationError):
            LeadForm(nombre="Juan", email="a@b.com", mensaje="")

    def test_mensaje_too_long(self):
        with pytest.raises(ValidationError):
            LeadForm(
                nombre="Juan",
                email="a@b.com",
                mensaje="X" * 2001,
            )


# ── LeadResponse ────────────────────────────────────────────────────

class TestLeadResponse:
    """Validación del modelo de respuesta."""

    def test_ok_response(self):
        resp = LeadResponse(status="ok", lead_id="rec123", detail="Todo bien.")
        assert resp.status == "ok"
        assert resp.lead_id == "rec123"

    def test_error_response_without_id(self):
        resp = LeadResponse(status="error", detail="Falló algo.")
        assert resp.lead_id is None
