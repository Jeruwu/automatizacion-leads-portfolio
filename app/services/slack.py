"""Servicio de notificación a Slack vía Incoming Webhook."""

from __future__ import annotations

import logging

import httpx

from app.config import settings
from app.models import LeadForm

logger = logging.getLogger(__name__)


class SlackError(Exception):
    """Error al enviar notificación a Slack."""


def _build_message(lead: LeadForm, airtable_id: str) -> dict:
    """Construye el payload de Slack con Block Kit.

    Parameters
    ----------
    lead : LeadForm
        Datos del lead.
    airtable_id : str
        ID del registro en Airtable.

    Returns
    -------
    dict
        Payload compatible con la API de Slack.
    """
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚀 Nuevo Lead Recibido",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Nombre:*\n{lead.nombre}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{lead.email}",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Mensaje:*\n>{lead.mensaje}",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📎 Registro Airtable: `{airtable_id}`",
                    },
                ],
            },
            {"type": "divider"},
        ],
    }


async def send_notification(lead: LeadForm, airtable_id: str) -> bool:
    """Envía una notificación a Slack con los datos del lead.

    En modo *dry-run* imprime el mensaje formateado en consola.

    Parameters
    ----------
    lead : LeadForm
        Datos del lead.
    airtable_id : str
        ID del registro creado en Airtable.

    Returns
    -------
    bool
        ``True`` si la notificación se envió (o simuló) correctamente.

    Raises
    ------
    SlackError
        Si la llamada al webhook falla.
    """
    payload = _build_message(lead, airtable_id)

    if settings.DRY_RUN:
        logger.info(
            "[DRY-RUN] Se habría enviado a Slack:\n"
            "  Webhook: <SLACK_WEBHOOK_URL>\n"
            "  Nombre : %s\n"
            "  Email  : %s\n"
            "  Mensaje: %s\n"
            "  Airtable ID: %s",
            lead.nombre,
            lead.email,
            lead.mensaje,
            airtable_id,
        )
        return True

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.SLACK_WEBHOOK_URL,
                json=payload,
            )
            response.raise_for_status()
            return True
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise SlackError(f"Error al notificar en Slack: {exc}") from exc
