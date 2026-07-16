"""Aplicación FastAPI — punto de entrada de la automatización de leads."""

from __future__ import annotations

import logging

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import LeadForm, LeadResponse
from app.services.airtable import create_record
from app.services.slack import send_notification

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Automatización de Leads",
    description=(
        "Recibe leads desde un formulario, los registra en Airtable "
        "y envía una notificación a Slack."
    ),
    version="1.0.0",
)


@app.get("/health", tags=["infra"])
async def health() -> dict[str, str]:
    """Health-check básico."""
    return {"status": "ok", "dry_run": str(settings.DRY_RUN).lower()}


@app.post(
    "/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["leads"],
    summary="Registrar un nuevo lead",
)
async def receive_lead(lead: LeadForm) -> LeadResponse:
    """Recibe datos de un formulario, los guarda en Airtable y notifica en Slack.

    Parameters
    ----------
    lead : LeadForm
        Datos del lead validados por Pydantic.

    Returns
    -------
    LeadResponse
        Resultado del procesamiento.
    """
    logger.info("Nuevo lead recibido: %s <%s>", lead.nombre, lead.email)

    # 1. Insertar en Airtable
    try:
        record = await create_record(lead)
        lead_id: str = record.get("id", "unknown")
        logger.info("Registro creado en Airtable: %s", lead_id)
    except Exception as exc:
        logger.error("Error al crear registro en Airtable: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=LeadResponse(
                status="error",
                lead_id=None,
                detail=f"Error al registrar en Airtable: {exc}",
            ).model_dump(),
        )

    # 2. Notificar en Slack
    try:
        await send_notification(lead, lead_id)
        logger.info("Notificación de Slack enviada.")
    except Exception as exc:
        # El lead ya está registrado; loggear pero no fallar.
        logger.warning("No se pudo notificar en Slack: %s", exc)

    return LeadResponse(
        status="ok",
        lead_id=lead_id,
        detail="Lead registrado y notificación enviada.",
    )
