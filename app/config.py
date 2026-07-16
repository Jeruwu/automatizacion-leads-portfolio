"""Configuración centralizada cargada desde variables de entorno."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto (si existe)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    """Valores de configuración leídos desde variables de entorno.

    Atributos
    ---------
    AIRTABLE_API_KEY : str
        Token personal de acceso a Airtable.
    AIRTABLE_BASE_ID : str
        ID de la base de Airtable (empieza con ``app``).
    AIRTABLE_TABLE_NAME : str
        Nombre de la tabla donde se insertan los leads.
    SLACK_WEBHOOK_URL : str
        URL del Incoming Webhook de Slack.
    DRY_RUN : bool
        Si es ``True``, no se realizan llamadas reales a APIs externas.
    """

    def __init__(self) -> None:
        self.AIRTABLE_API_KEY: str = os.getenv("AIRTABLE_API_KEY", "")
        self.AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")
        self.AIRTABLE_TABLE_NAME: str = os.getenv("AIRTABLE_TABLE_NAME", "Leads")
        self.SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
        self.DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")


settings = Settings()
