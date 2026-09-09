# CareRoute

CareRoute is a team-built prototype for coordinating a medical-travel itinerary across flight, voice, notification, lodging, and appointment workflows. This repository contains the central FastAPI orchestrator and integration scaffolding.

## Project ownership

This is a collaborative repository; it should not be presented as the work of one contributor. Rohan Chavan's independently maintained contribution is the [CareRoute Flight Agent](https://github.com/RohanChavan0701/careroute-flight-agent), a standalone FastAPI service that exposes provider-backed flight status through an A2A-style JSON-RPC interface.

Related team components:

- [Flutter client](https://github.com/ForgottenLight4415/codefest-25-app)
- [Notification and voice services](https://github.com/uma1902/notification-system)
- [Original orchestrator repository](https://github.com/atharvasalunke/medical_orchestrator)

![CareRoute orchestrator architecture](docs/architecture-diagram.png)

## What this repository contains

- `backend/main_backend.py`: FastAPI endpoints for booking, trip status, flight status, voice requests, notifications, FCM, and service health
- `backend/orchestrator.py`: workflow coordination and HTTP clients for external agents
- `backend/scheduler.py`: APScheduler jobs for reminders, flight updates, arrival monitoring, and orchestration cleanup
- `backend/knowledge_base.py`: in-memory patient-context store with optional LLM responses and encrypted values
- `backend/database/`: SQLAlchemy models, repository, migrations, audit helpers, and encryption utilities; startup falls back when the configured database is unavailable
- `agents/`: legacy/local agent adapters retained from the prototype
- `deploy/` and `aws/`: Docker and AWS deployment scaffolding
- `tests/`: unit, endpoint, workflow, and opt-in external integration checks

## Runtime shape

```text
Flutter or API client
        │
        ▼
FastAPI orchestrator ──► booking and trip state
        │
        ├──► Flight Agent
        ├──► Voice Agent
        └──► Notification Agent
        │
        └──► scheduler + optional database/FCM integrations
```

External service locations are configuration, not repository constants. Set `FLIGHT_AGENT_URL`, `VOICE_AGENT_URL`, and `NOTIFICATION_AGENT_URL` for the services you intend to call. `HOTEL_AGENT_URL` and `HOSPITAL_AGENT_URL` configure the corresponding adapters.

## Run locally

Python 3.11+ is recommended.

```bash
git clone https://github.com/RohanChavan0701/CareRoute.git
cd CareRoute
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r backend/requirements.txt
export DATABASE_URL="postgresql://guardian:local-password@localhost:5432/guardian"
python3 -m uvicorn backend.main_backend:app --host 127.0.0.1 --port 8000
```

Once running:

- API root: `http://localhost:8000/`
- Health check: `http://localhost:8000/health`
- OpenAPI UI: `http://localhost:8000/docs`

`DATABASE_URL` is required when the backend modules are imported. If that configured database is unreachable, startup logs a fallback and request paths can use the prototype's local state. Workflows that call external agents still require reachable endpoints and whatever credentials those services expect.

## Configuration and data handling

Keep credentials in environment variables or a local `.env` file; `.env` is gitignored.

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection used by the database layer |
| `FLIGHT_AGENT_URL` | Flight Agent A2A endpoint |
| `VOICE_AGENT_URL` | Voice Agent JSON-RPC endpoint |
| `NOTIFICATION_AGENT_URL` | Notification service endpoint |
| `OPENAI_API_KEY` | Optional knowledge-base LLM responses |
| `HIPAA_ENCRYPTION_PASSWORD` | Stable knowledge-base encryption key derivation |
| `HIPAA_ENCRYPTION_SALT` | Optional deployment-specific derivation salt |

If `HIPAA_ENCRYPTION_PASSWORD` is absent, the in-memory knowledge base uses an ephemeral process-local key and warns at startup; it no longer creates or reads a repository key file. The repository includes security-oriented utilities, but it has not been audited or certified for regulated or production use.

## Selected endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/booking` | Create a booking and start orchestration |
| `GET /guardian/trip/status/{user_id}` | Read the assembled trip status |
| `POST /api/flight/status` | Forward a flight-status request |
| `POST /guardian/voice/call` | Forward a voice-agent request with trip context |
| `POST /api/notifications/hotel-booking` | Send a hotel-booking notification request |
| `GET /guardian/scheduler/status` | Inspect scheduler state |
| `GET /health` | Service health response |

## Tests

From the repository root:

```bash
python3 -m pytest -q
```

Tests named for real or complete external flows may require live agent endpoints and should be treated as opt-in integration checks. The local suite and mock-backed paths are the appropriate starting point for repository verification.

## Prototype limitations

- External agents are separately deployed services and are not bundled here.
- Several workflows fall back to local JSON/in-memory state when database services are unavailable.
- Sample data is synthetic, but the system models sensitive fields; do not use real patient data in an unreviewed deployment.
- Deployment scripts are scaffolding. This README intentionally does not claim an active public endpoint, regulatory compliance, production readiness, or measured performance.
