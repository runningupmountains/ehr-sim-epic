# EHR Simulator — Epic-style

A lightweight external EHR simulator built with FastAPI and PostgreSQL. Designed to be called by an external integration layer (e.g., ConnectHub) as if it were a real client Epic system. Used for integration testing and demos only.

This project has no connection to the Curosana database. All chart data lives entirely in its own separate Postgres database.

Live and fully operational. Here's the summary:

Deployed: ehr-sim-epic-dev
URL: https://tfpkasbci3.us-west-2.awsapprunner.com
DOCS: https://tfpkasbci3.us-west-2.awsapprunner.com/docs
Region: us-west-2

## Resource	Name
App Runner service	ehr-sim-epic-dev
ECR repository	ehr-sim-epic-dev
IAM role	AppRunnerECRAccessRole
RDS database	ehr_sim_epic (existing)

## To redeploy after code changes:

docker buildx build --platform linux/amd64 \
  --tag 710074042372.dkr.ecr.us-west-2.amazonaws.com/ehr-sim-epic-dev:latest \
  --push .

aws apprunner start-deployment \
  --service-arn arn:aws:apprunner:us-west-2:710074042372:service/ehr-sim-epic-dev/8c086113edd74aeba3a579fc7286e964 \
  --region us-west-2
ConnectHub can now point at https://tfpkasbci3.us-west-2.awsapprunner.com with x-api-key: eh8ce6b5e92b412fb4c46c8817dde122.

---

## Project Structure

```
ehr-sim-epic/
├── app/
│   ├── main.py          # FastAPI app, middleware, router wiring
│   ├── config.py        # Settings via pydantic-settings + .env
│   ├── db.py            # SQLAlchemy engine and session factory
│   ├── deps.py          # Shared FastAPI dependencies (DB session, API key auth)
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic response schemas
│   ├── routes/          # FastAPI route handlers
│   └── services/        # Query logic (kept separate from routes)
├── scripts/
│   ├── init_db.py       # Creates all tables via SQLAlchemy metadata
│   └── seed_data.py     # Populates the DB with deterministic mock data
├── sql/
│   └── schema.sql       # Raw SQL schema (alternative to init_db.py)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Local Setup

### 1. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the server

```bash
uvicorn app.main:app --reload --port 8001
```

API docs available at: `http://localhost:8001/docs`

---

## Authentication

All `/api/epic/v1/*` endpoints require the `x-api-key` header:

```
x-api-key: dev-ehr-sim-key-change-in-production
```

Set the key in `.env` as `API_KEY=...`. ConnectHub should store this key as an environment secret.

A stub for future OAuth2 support is noted in `.env.example`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth required) |
| GET | `/api/epic/v1/patients` | List/search patients (`?mrn=`, `?last_name=`, `?limit=`, `?offset=`) |
| GET | `/api/epic/v1/patients/{patient_id}` | Get patient by UUID |
| GET | `/api/epic/v1/patients/{patient_id}/chart` | Full aggregated chart |
| GET | `/api/epic/v1/patients/{patient_id}/encounters` | Patient encounters (`?since=`, `?limit=`) |
| GET | `/api/epic/v1/patients/{patient_id}/notes` | Patient clinical notes |
| GET | `/api/epic/v1/patients/{patient_id}/labs` | Patient lab results |
| GET | `/api/epic/v1/patients/{patient_id}/allergies` | Patient allergy list |
| GET | `/api/epic/v1/patients/{patient_id}/documents` | Patient documents |
| GET | `/api/epic/v1/encounters/{encounter_id}` | Single encounter by UUID |
| GET | `/api/epic/v1/encounters/{encounter_id}/notes` | Notes for an encounter |
| GET | `/api/epic/v1/providers` | List providers |
| GET | `/api/epic/v1/providers/{provider_id}` | Single provider by UUID |

---

## curl Examples

Set these environment variables first for convenience:

```bash
export BASE=http://localhost:8001
export KEY=eh8ce6b5e92b412fb4c46c8817dde122
```

### Health check

```bash
curl $BASE/health
```

### List all patients

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients"
```

### Search by last name

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients?last_name=Hartley"
```

### Search by MRN (Epic-style)

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients?mrn=E100001"
```

### Get patient by ID

```bash
# First, retrieve the patient_id from the search above, then:
PATIENT_ID=<uuid-from-above>

curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients/$PATIENT_ID"
```

### Full chart retrieval

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients/$PATIENT_ID/chart" | python3 -m json.tool
```

### Patient encounters (with date filter)

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients/$PATIENT_ID/encounters?since=2025-01-01"
```

### Patient labs

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients/$PATIENT_ID/labs"
```

### Patient documents

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients/$PATIENT_ID/documents"
```

### Patient clinical notes

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/patients/$PATIENT_ID/notes"
```

### Encounter notes (by encounter ID)

```bash
ENCOUNTER_ID=<uuid-of-encounter>

curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/encounters/$ENCOUNTER_ID/notes"
```

### List providers

```bash
curl -H "x-api-key: $KEY" "$BASE/api/epic/v1/providers"
```

---

## Chart Response Shape

`GET /api/epic/v1/patients/{patient_id}/chart` returns:

```json
{
  "patient": { ... },
  "primary_provider": { ... },
  "recent_encounters": [ ... ],
  "clinical_notes": [ ... ],
  "medications": [ ... ],
  "allergies": [ ... ],
  "problems": [ ... ],
  "lab_results": [ ... ],
  "documents": [ ... ]
}
```

---

## Seeded Mock Patient Personas

30 deterministic patients across multiple specialties:

| MRN | Name | Age/Sex | Primary Condition(s) | Primary Provider |
|-----|------|---------|----------------------|-----------------|
| E100001 | Eleanor Hartley | 70F | Hypertension, hyperlipidemia, osteoarthritis | Dr. Nguyen (Internal Medicine) |
| E100002 | Marcus Williams | 47M | Type 2 diabetes, hypertension, obesity | Dr. Nguyen |
| E100003 | Sofia Reyes | 35F | Annual wellness (no chronic conditions) | Dr. Nguyen |
| E100004 | James Thornton | 74M | CHF, COPD, hypertension | Dr. Okafor (Cardiology) |
| E100005 | Priya Patel | 57F | Hypertension, type 2 diabetes | Dr. Nguyen |
| E100006 | David Chen | 30M | Viral URI (acute) | Dr. Santos (Urgent Care) |
| E100007 | Margaret Foster | 80F | Diastolic CHF, atrial fibrillation, polypharmacy | Dr. Okafor |
| E100008 | Carlos Rivera | 52M | Knee osteoarthritis, pre-op TKA | Dr. Thornton (Orthopedics) |
| E100009 | Aisha Johnson | 37F | Acne vulgaris, compound nevus | Dr. Kim (Dermatology) |
| E100010 | Robert Kim | 64M | CAD, post-MI, hyperlipidemia | Dr. Okafor |
| E100011 | Patricia Gonzalez | 42F | Annual wellness | Dr. Nguyen |
| E100012 | Thomas Anderson | 79M | Atrial fibrillation, CAD | Dr. Okafor |
| E100013 | Mei Zhang | 24F | Atopic dermatitis | Dr. Kim |
| E100014 | Anthony Harris | 55M | Asthma | Dr. Nguyen |
| E100015 | Linda Murphy | 66F | COPD, hypertension | Dr. Morrison (Pulmonology) |
| E100016 | Kevin Wallace | 40M | Lumbar disc herniation | Dr. Thornton |
| E100017 | Diane Scott | 73F | Hypothyroidism | Dr. Patel (Endocrinology) |
| E100018 | Michael Brown | 45M | Annual wellness | Dr. Nguyen |
| E100019 | Sandra Taylor | 62F | Anxiety, insomnia | Dr. Nguyen |
| E100020 | George White | 87M | Peripheral artery disease | Dr. Okafor |
| E100021 | Amanda Lewis | 28F | Ankle sprain (acute) | Dr. Santos |
| E100022 | Brian Walker | 60M | Shoulder impingement | Dr. Thornton |
| E100023 | Helen Hall | 76F | Idiopathic pulmonary fibrosis | Dr. Morrison |
| E100024 | Steven Young | 49M | Type 2 diabetes, hypothyroidism | Dr. Nguyen |
| E100025 | Nancy Allen | 68F | Type 2 diabetes | Dr. Patel |
| E100026 | Daniel King | 36M | Seborrheic dermatitis | Dr. Kim |
| E100027 | Sharon Wright | 81F | Cardiac (unspecified) | Dr. Okafor |
| E100028 | Jason Lopez | 32M | Annual wellness | Dr. Nguyen |
| E100029 | Donna Hill | 58F | Orthopedic (unspecified) | Dr. Thornton |
| E100030 | Raymond Green | 72M | CAD follow-up | Dr. Okafor |

---

## How ConnectHub Would Integrate With This

ConnectHub (the integration layer) treats this simulator as if it were a real client Epic system accessed via an integration engine or direct API.

### Step 1 — Store the connection config

ConnectHub stores the simulator base URL and API key as a client EHR connection record:

```json
{
  "client_id": "demo-clinic-001",
  "ehr_type": "epic_sim",
  "base_url": "http://localhost:8001",
  "api_key": "dev-ehr-sim-key-change-in-production"
}
```

### Step 2 — Patient lookup by MRN

When RevIQ or a user triggers a chart pull, ConnectHub calls:

```
GET /api/epic/v1/patients?mrn=E100001
x-api-key: <key>
```

ConnectHub maps the returned `patient_id` UUID for subsequent calls.

### Step 3 — Full chart pull

```
GET /api/epic/v1/patients/{patient_id}/chart
x-api-key: <key>
```

ConnectHub receives the aggregated chart JSON and routes each section (encounters, notes, labs, medications, etc.) through its internal processing pipeline — without storing raw chart data in the Curosana core database.

### Step 4 — Incremental sync (encounter-level)

For ongoing sync, ConnectHub polls:

```
GET /api/epic/v1/patients/{patient_id}/encounters?since=2025-01-01
GET /api/epic/v1/patients/{patient_id}/labs?since=2025-01-01
```

### Step 5 — Encounter drill-down

For document retrieval or note processing:

```
GET /api/epic/v1/encounters/{encounter_id}/notes
GET /api/epic/v1/patients/{patient_id}/documents
```

---

## Why This Helps Avoid Storing Client Chart Data in Curosana Core

Real client EHR chart data (patient demographics, clinical notes, medications, lab results) is protected health information (PHI). Curosana's internal database should not be a long-term store for raw client chart records — only for the outputs of its own AI processing.

This simulator makes that architecture explicit:

1. **All chart data lives in the external system.** The simulator's Postgres database is completely separate — a different host, a different database name, no shared connection strings.

2. **ConnectHub calls out, not in.** The integration layer fetches chart data on demand from the EHR simulator (or in production, from the real Epic system). It does not import chart records into Curosana tables.

3. **Curosana stores results, not source data.** After ConnectHub retrieves a chart and RevIQ processes it, Curosana stores only the AI-generated outputs (e.g., prior auth decisions, denial predictions, summarized insights) — not the underlying clinical records.

4. **The boundary is enforced at the API level.** There is no shared database pool, no ORM cross-reference, and no foreign keys that would allow Curosana models to join against chart tables.

5. **Demo and test parity.** Using this simulator in demos and integration tests means ConnectHub's code paths are tested exactly as they will run against a real Epic system — the only difference is the base URL.

---

## Future Enhancements

- **FHIR-lite endpoints** — thin wrapper over the same data returning R4-shaped JSON
- **OAuth2 client credentials flow** — stub is already noted in `.env.example`
- **CSN-based lookup** — `GET /api/epic/v1/encounters?csn=CSN-10001`
- **Docker Compose** — `docker-compose.yml` with the FastAPI app + Postgres container
- **Webhook simulation** — outbound ADT/results notifications to test ConnectHub event ingestion
