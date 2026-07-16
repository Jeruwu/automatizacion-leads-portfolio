"""Modelos Pydantic para validación de datos de entrada y respuesta."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LeadForm(BaseModel):
    """Datos de un nuevo lead proveniente de un formulario.

    Attributes
    ----------
    nombre : str
        Nombre completo del lead (mín. 1, máx. 120 caracteres).
    email : EmailStr
        Correo electrónico válido.
    mensaje : str
        Texto del mensaje o consulta (mín. 1, máx. 2000 caracteres).
    """

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=120,
        examples=["María López"],
        description="Nombre completo del lead",
    )
    email: EmailStr = Field(
        ...,
        examples=["maria@ejemplo.com"],
        description="Correo electrónico de contacto",
    )
    mensaje: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["Me interesa contratar sus servicios de automatización."],
        description="Mensaje o consulta del lead",
    )


class LeadResponse(BaseModel):
    """Respuesta devuelta tras procesar un lead.

    Attributes
    ----------
    status : str
        Estado del procesamiento ("ok" o "error").
    lead_id : str | None
        ID del registro creado en Airtable (``None`` si falló).
    detail : str
        Mensaje descriptivo del resultado.
    """

    status: str = Field(..., examples=["ok"])
    lead_id: str | None = Field(None, examples=["recABC123"])
    detail: str = Field(..., examples=["Lead registrado y notificación enviada."])
