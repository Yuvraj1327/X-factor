# Visarjan Ghat Watch — Backend

**Bhopal Impact Lab · Track 2 · BMC Admin Dashboard + WhatsApp Citizen Service**

A FastAPI backend that analyses water-quality data for seven Bhopal ghats,
provides a BMC officer dashboard, and delivers verified advisories to citizens
over WhatsApp. Built for the Visarjan 2025 campaign.

---

## Important Disclaimers

> **Data-based priority indicators — not safety certifications.**
> Rankings and analyses are derived from available historical data only.
> They do not certify current water quality or official safety status.
> All readings are labelled with their sampling date and data source.
> Missing data is flagged explicitly and never assumed to be within safe limits.

> **Official advisories require BMC officer approval** before publication.
> Only approved, signed-off advisories reach citizens via WhatsApp.

---

## Architecture

```
CSV datasets
    │
    ▼
app/analysis/  ← CPCB rules + risk ranking engine
    │
    ▼
app/api/v1/
  ├── auth.py         ← JWT login (admin only)
  ├── ghats.py        ← Ghat data endpoints (public read)
  ├── analysis.py     ← Rankings and summary
  ├── admin.py        ← BMC dashboard (protected)
  └── whatsapp.py     ← Webhook + citizen service
    │
    ▼
Meta WhatsApp Cloud API  ←→  Citizens
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL, JWT_SECRET_KEY, etc.
openssl rand -hex 32   # Use output as JWT_SECRET_KEY
```

### 4. Run database migrations

```bash
export DATABASE_URL_SYNC=postgresql+psycopg2://postgres:yourpassword@localhost:5432/ghatwatch
alembic upgrade head
```

### 5. Create the first admin

```bash
export BOOTSTRAP_ADMIN_EMAIL=admin@bmc.gov.in
export BOOTSTRAP_ADMIN_PASSWORD=YourSecurePassword123!
python -m app.scripts.create_admin
```

### 6. Import official data (optional)

Place CSV files in `data/` (see `data/README.md`), then:

```bash
python -m app.scripts.import_data
```

### 7. Run the development server

```bash
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs (development mode only)

---

## Docker

```bash
cp .env.example .env  # Fill in values
JWT_SECRET_KEY=$(openssl rand -hex 32)

docker compose up -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.create_admin
```

---

## Key Endpoints

### Authentication
| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/v1/auth/login` | Admin login → JWT |
| `GET`  | `/api/v1/auth/me` | Current admin profile |

### Ghats (public)
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/v1/ghats` | List active ghats |
| `GET` | `/api/v1/ghats/{id}` | Ghat detail + latest readings |
| `GET` | `/api/v1/ghats/{id}/history` | Historical trend data |
| `GET` | `/api/v1/analysis/summary` | Overall data summary |
| `GET` | `/api/v1/analysis/rankings` | Evidence-based risk rankings |
| `GET` | `/api/v1/sources` | Official data sources |

### BMC Admin Dashboard (JWT required)
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/v1/admin/dashboard` | Summary + top-priority ghats |
| `GET` | `/api/v1/admin/advisories` | List advisories |
| `POST` | `/api/v1/admin/advisories` | Create draft |
| `PATCH` | `/api/v1/admin/advisories/{id}` | Update draft |
| `POST` | `/api/v1/admin/advisories/{id}/approve` | Approve (officer only) |
| `POST` | `/api/v1/admin/advisories/{id}/send` | Send to WhatsApp subscribers |
| `GET` | `/api/v1/admin/advisories/{id}/delivery-status` | Delivery stats |
| `GET` | `/api/v1/admin/whatsapp/messages` | Message history |

### WhatsApp Webhook
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/v1/whatsapp/webhook` | Meta verification challenge |
| `POST` | `/api/v1/whatsapp/webhook` | Incoming messages + delivery updates |

---

## WhatsApp Citizen Commands

| Command | Action |
|---------|--------|
| `HI` | Welcome message + command list |
| `HELP` | Available commands |
| `GHAT` | List monitored ghats |
| `<Ghat Name>` | Latest readings + source reference |
| `ALERTS` | Recent BMC-approved advisories |
| `SUBSCRIBE` | Opt in to proactive alerts |
| `STOP` | Unsubscribe |

*Hindi commands: नमस्ते, मदद, घाट, अलर्ट, सदस्यता, रुकें*

---

## Environment Variables

See `.env.example` for the full list with comments.

**Never commit `.env` or any file with real credentials.**

### Required for production

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Async PostgreSQL URL (asyncpg) |
| `DATABASE_URL_SYNC` | Sync PostgreSQL URL (psycopg2, for Alembic) |
| `JWT_SECRET_KEY` | 32+ byte random hex string |
| `WHATSAPP_ACCESS_TOKEN` | Meta Cloud API token |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp Business phone number ID |
| `WHATSAPP_APP_SECRET` | Used to verify webhook signatures |
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | Random token for Meta webhook setup |

### Safety defaults

| Variable | Default | Notes |
|----------|---------|-------|
| `WHATSAPP_DRY_RUN` | `true` | **Never set false without Meta approval** |
| `DATA_FRESHNESS_THRESHOLD_DAYS` | `90` | Advisories with older data are blocked |

---

## Running Tests

```bash
pip install aiosqlite  # Required for SQLite test DB
pytest -v --tb=short
```

Tests run against an in-memory SQLite database — no PostgreSQL needed.

Coverage:
- CPCB threshold rules and risk scoring
- Missing data precautionary penalty
- Admin authentication and JWT
- Advisory approval workflow + stale-data blocking
- Role-based access (analysts cannot approve)
- WhatsApp dry-run default
- Subscriber consent requirements
- Duplicate webhook event deduplication
- Ghat history disclaimer presence

---

## Official Data

The analysis engine uses CPCB Class B (bathing/outdoor contact) benchmarks.

Default thresholds (configurable via DB):

| Parameter | Class B Limit |
|-----------|---------------|
| Dissolved Oxygen | ≥ 5 mg/L |
| BOD | ≤ 3 mg/L |
| pH | 6.5 – 8.5 |
| Fecal Coliform | ≤ 500 MPN/100mL |
| Total Coliform | ≤ 5000 MPN/100mL |

Source: IS 2296:1982 / CPCB Designated Best Use Classification

Official datasets should be placed in `data/` — see `data/README.md`.

---

## Meta WhatsApp API Setup

1. Create a Meta App at [developers.facebook.com](https://developers.facebook.com)
2. Enable WhatsApp Business API
3. Get your Phone Number ID and Business Account ID
4. Create approved message templates: `ghat_advisory_en`, `ghat_advisory_hi`
5. Configure the webhook URL: `https://your-domain.com/api/v1/whatsapp/webhook`
6. Set `WHATSAPP_WEBHOOK_VERIFY_TOKEN` to match your Meta app settings
7. Set `WHATSAPP_DRY_RUN=false` **only after templates are approved**

---

## Advisory Workflow

```
Admin creates draft
        │
        ▼
Admin reviews evidence (readings + source references)
        │
        ▼
BMC Officer approves  ←──── Stale data (>90 days) blocks approval
        │
        ▼
Officer clicks "Send"
        │
        ▼
System broadcasts to opted-in subscribers (per ghat preference)
        │
        ▼
Delivery events tracked via Meta webhooks (idempotent)
```

---

## Project Structure

```
app/
├── main.py               Application entry point
├── api/
│   └── v1/
│       ├── auth.py       Authentication
│       ├── ghats.py      Ghat endpoints
│       ├── analysis.py   Rankings and summary
│       ├── admin.py      BMC admin dashboard
│       └── whatsapp.py   Webhook
├── core/
│   ├── config.py         Settings (pydantic-settings)
│   ├── security.py       JWT + bcrypt
│   ├── logging.py        Structured logging (PII redacted)
│   └── exceptions.py     Domain exceptions
├── models/               SQLAlchemy models
├── schemas/              Pydantic request/response schemas
├── repositories/         Database access layer
├── services/
│   ├── advisory_service.py   Advisory workflow
│   ├── citizen_service.py    WhatsApp citizen responses
│   └── whatsapp_client.py    Meta API client
├── analysis/
│   ├── cpcb_rules.py     CPCB Class B thresholds
│   ├── engine.py         Risk scoring and ranking
│   └── data_import.py    CSV import utility
├── scripts/
│   ├── create_admin.py   Bootstrap first admin
│   └── import_data.py    Import CSV datasets
└── database/
    └── session.py        Async SQLAlchemy engine
alembic/
└── versions/
    └── 0001_initial.py   Full schema migration
tests/
├── conftest.py           Fixtures (in-memory SQLite)
├── test_cpcb_rules.py
├── test_auth.py
├── test_advisory.py
├── test_whatsapp.py
└── test_ghats.py
data/
└── README.md             Dataset format documentation
```

---

## Security Notes

- Passwords are hashed with bcrypt
- JWT secrets are read from environment (never hardcoded)
- WhatsApp webhook signatures are verified via HMAC-SHA256
- Logs automatically redact Bearer tokens and phone numbers
- `/docs` (Swagger) is disabled in production (`DEBUG=false`)
- Admin creation is CLI-only — no public registration endpoint
- Dry-run mode is the default — accidental sends are prevented

---

*Built for Bhopal Impact Lab, Track 2 · Visarjan Ghat Watch · 2025*
