# 🚀 Automatización de Leads — Formulario → Airtable → Slack

## ¿Qué problema resuelve?

En muchos negocios, los leads que llegan desde formularios web se pierden o tardan horas en ser atendidos porque dependen de que alguien revise manualmente una bandeja de entrada o una hoja de cálculo.

**Esta automatización elimina ese cuello de botella**: cada vez que un potencial cliente llena un formulario, sus datos se registran automáticamente en Airtable (como CRM) y se envía una notificación instantánea a un canal de Slack para que el equipo de ventas pueda responder en minutos, no en horas.

---

## Diagrama del flujo

```
┌─────────────┐     POST /leads     ┌──────────┐     API REST     ┌───────────┐
│  Formulario │ ──────────────────▶ │  FastAPI  │ ──────────────▶ │  Airtable │
│  (webhook)  │                     │  Server   │                 │  (CRM)    │
└─────────────┘                     └─────┬─────┘                 └───────────┘
                                          │
                                          │  Incoming Webhook
                                          ▼
                                    ┌───────────┐
                                    │   Slack   │
                                    │  (canal)  │
                                    └───────────┘
```

1. Un formulario (Google Forms, Typeform, o cualquier frontend) envía un `POST` con los datos del lead.
2. **FastAPI** valida los datos, los inserta en una tabla de **Airtable** vía su API REST.
3. Envía una notificación formateada a un canal de **Slack** vía Incoming Webhook.
4. Si Airtable falla, se reintenta automáticamente (hasta 3 veces con backoff exponencial).

---

## Estructura del proyecto

```
automatizacion-leads-portfolio/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuración desde variables de entorno
│   ├── main.py            # App FastAPI (endpoints /leads, /health)
│   ├── models.py          # Modelos Pydantic (LeadForm, LeadResponse)
│   └── services/
│       ├── __init__.py
│       ├── airtable.py    # Integración con Airtable (reintentos, dry-run)
│       └── slack.py       # Notificación a Slack (Block Kit, dry-run)
├── tests/
│   ├── __init__.py
│   ├── test_api.py        # Tests del endpoint
│   ├── test_models.py     # Tests de validación Pydantic
│   └── test_services.py   # Tests de servicios en dry-run
├── .env.example           # Plantilla de variables de entorno
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Configuración de credenciales

### 1. Airtable

1. Crea una cuenta en [airtable.com](https://airtable.com).
2. Crea una base con una tabla llamada `Leads` con estas columnas:
   - `Nombre` (Single line text)
   - `Email` (Email)
   - `Mensaje` (Long text)
   - `Fecha` (Date)
3. Obtén tu **Personal Access Token** desde [airtable.com/create/tokens](https://airtable.com/create/tokens) con permisos de escritura.
4. Copia el **Base ID** desde la URL de tu base (`https://airtable.com/appXXXXXXXX/...`).

### 2. Slack

1. Crea una app en [api.slack.com/apps](https://api.slack.com/apps).
2. Activa **Incoming Webhooks** y crea uno para el canal deseado.
3. Copia la **Webhook URL** (`https://hooks.slack.com/services/T.../B.../XXX`).

### 3. Variables de entorno

Copia el archivo de ejemplo y rellena tus credenciales:

```bash
cp .env.example .env
```

Edita `.env`:

```env
AIRTABLE_API_KEY=patXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_TABLE_NAME=Leads
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXX
DRY_RUN=false
```

> ⚠️ **Nunca subas el archivo `.env` a git.** Ya está incluido en `.gitignore`.

---

## Cómo correr el proyecto

### Requisitos previos

- Python 3.11+
- pip

### Instalación

```bash
pip install -r requirements.txt
```

### Ejecutar en modo dry-run (sin credenciales reales)

```bash
DRY_RUN=true uvicorn app.main:app --reload
```

En Windows (PowerShell):

```powershell
$env:DRY_RUN="true"; uvicorn app.main:app --reload
```

### Ejecutar con APIs reales

```bash
DRY_RUN=false uvicorn app.main:app --reload
```

### Probar con curl

```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "María López",
    "email": "maria@ejemplo.com",
    "mensaje": "Me interesa una automatización para mi negocio."
  }'
```

También puedes usar la documentación interactiva en: **http://localhost:8000/docs**

---

## Cómo ejecutar tests

```bash
pytest tests/ -v
```

Todos los tests corren en modo dry-run automáticamente — no necesitan credenciales reales.

---

## Stack técnico

| Tecnología | Uso |
|---|---|
| **Python 3.11+** | Lenguaje principal |
| **FastAPI** | Framework web / endpoint REST |
| **Pydantic v2** | Validación de datos |
| **httpx** | Cliente HTTP async |
| **python-dotenv** | Carga de variables de entorno |
| **pytest** | Testing |
| **Airtable API** | CRM / base de datos de leads |
| **Slack Webhooks** | Notificaciones al equipo |

---

## Licencia

MIT
