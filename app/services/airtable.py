"""Servicio de integración con la API REST de Airtable."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.models import LeadForm

logger = logging.getLogger(__name__)

AIRTABLE_URL = "https://api.airtable.com/v0/{base_id}/{table_name}"

MAX_RETRIES = 3
BACKOFF_BASE = 1  # segundos


class AirtableError(Exception):
    """Error al comunicarse con la API de Airtable."""


async def _post_with_retries(url: str, headers: dict, json_body: dict) -> dict:
    """POST a Airtable con reintentos y backoff exponencial.

    Parameters
    ----------
    url : str
        URL completa del endpoint de Airtable.
    headers : dict
        Headers HTTP (incluye Authorization).
    json_body : dict
        Cuerpo JSON a enviar.

    Returns
    -------
    dict
        Respuesta JSON de Airtable.

    Raises
    ------
    AirtableError
        Si se agotan los reintentos.
    """
    last_exc: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=json_body)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            last_exc = exc
            wait = BACKOFF_BASE * (2 ** (attempt - 1))
            logger.warning(
                "Airtable intento %d/%d falló: %s — reintentando en %ds",
                attempt,
                MAX_RETRIES,
                exc,
                wait,
            )
            await asyncio.sleep(wait)

    raise AirtableError(
        f"Fallo tras {MAX_RETRIES} intentos: {last_exc}"
    ) from last_exc


async def create_record(lead: LeadForm) -> dict:
    """Crea un registro de lead en Airtable.

    En modo *dry-run* imprime el payload y retorna un registro simulado.

    Parameters
    ----------
    lead : LeadForm
        Datos validados del lead.

    Returns
    -------
    dict
        Registro creado (real o simulado), con al menos la clave ``"id"``.
    """
    fields = {
        "Nombre": lead.nombre,
        "Email": lead.email,
        "Mensaje": lead.mensaje,
        "Fecha": datetime.now(timezone.utc).isoformat(),
    }

    if settings.DRY_RUN:
        fake_id = f"rec_dry_{uuid.uuid4().hex[:8]}"
        logger.info(
            "[DRY-RUN] Se habría enviado a Airtable:\n"
            "  URL: %s\n  Campos: %s",
            AIRTABLE_URL.format(
                base_id="<BASE_ID>", table_name="<TABLE>"
            ),
            fields,
        )
        return {"id": fake_id, "fields": fields}

    url = AIRTABLE_URL.format(
        base_id=settings.AIRTABLE_BASE_ID,
        table_name=settings.AIRTABLE_TABLE_NAME,
    )
    headers = {
        "Authorization": f"Bearer {settings.AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {"fields": fields}

    return await _post_with_retries(url, headers, body)
