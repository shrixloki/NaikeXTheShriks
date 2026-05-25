# Nayki Production Backend (nayki-backend)

Nayki is a serious, Android-first safety-navigation app by **The Shriks**. This repository contains the production-ready backend API foundation built using Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL + PostGIS, and Redis.

---

## ⚠️ Important Safety & Data Disclaimer
This is a high-fidelity safety intelligence product. 

1. **Strictly No Fake Safety Claims:** Under no circumstances should this API claim a route, location, or area is **"safe"** or **"secure"**. 
2. **Deterministic Risk Mapping:** Real-world metrics are mapped using:
   - `lower_risk` / `moderate_risk` / `higher_risk` / `unknown` (Risk Levels)
   - `confidence` (0.0 to 1.0)
   - `evidence_count` (Integer)
   - `coverage_status` (`unavailable`, `limited`, `moderate`, `strong`)
   - `risk_reasons` (`poor_lighting`, `recent_incident`, `isolated_road`, `limited_data`, `help_far_away`, `night_time`, `government_data`, `user_reports_unverified`)
3. **Data Absence Transparency:** If no safety evidence is available, the backend must return `coverage_status = "unavailable"`, `confidence = "low"`, and `safety_score = null`. **Never invent high-safety mock claims.**

---

## 🛠️ Technology Stack
- **Runtime:** Python 3.12
- **Framework:** FastAPI + Pydantic v2
- **ORM:** SQLAlchemy 2.x (asyncpg driver)
- **Migrations:** Alembic
- **Database:** PostgreSQL + PostGIS extension
- **Caching:** Redis 7
- **Dockerization:** Docker & docker-compose

---

## 📋 Environment Configuration
Create a `.env` file in the root directory based on `.env.example`:

| Variable | Description | Local Dev Default |
| :--- | :--- | :--- |
| `APP_ENV` | Application environment status (`local`, `production`) | `local` |
| `API_PORT` | Port number of the FastAPI server | `8000` |
| `DATABASE_URL` | Async PG Database URL (PostGIS) | `postgresql+asyncpg://nayki_user:nayki_password@localhost:5432/nayki_db` |
| `SYNC_DATABASE_URL` | Sync PG Database URL (Alembic) | `postgresql+psycopg://nayki_user:nayki_password@localhost:5432/nayki_db` |
| `REDIS_URL` | Redis cache connection string | `redis://localhost:6379/0` |
| `DEV_AUTH_ENABLED` | Toggle mock authentication bypass (local only) | `true` |
| `JWT_ISSUER` | Firebase token issuer url | `https://securetoken.google.com/nayki-production` |
| `FIREBASE_PROJECT_ID` | Firebase unique project ID | `nayki-production` |
| `H3_RESOLUTION` | Standard H3 grid resolution (e.g. resolution 9) | `9` |
| `LOG_LEVEL` | Application logging verbosity (`info`, `debug`, `error`) | `INFO` |

---

## 🚀 Getting Started

### 1. Running with Docker Compose (Recommended)
This launches PostgreSQL/PostGIS, Redis, and the FastAPI application in interconnected containers:

```bash
# Start all services with hot-reloading active
make dev
# Or directly
docker compose up --build
```

### 2. Running Local Commands (Native Python Environment)
If you wish to run/develop outside Docker, create a virtual environment first:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

To run local infrastructure on Docker and local application natively:
```bash
# Start postgres and redis in background
make db-up

# Apply Alembic Migrations
make migrate

# Launch hot-reload server
uvicorn app.main:app --reload --port 8000
```

---

## 💾 Database Migrations
Migrations are handled via Alembic. The system automatically provisions the `postgis` spatial extension before generating models.

```bash
# Apply pending migrations
make migrate
# Or directly
alembic upgrade head

# Generate a new migration script (if you alter model models)
alembic revision --autogenerate -m "describe_changes"
```

---

## 🧪 Running Tests
A comprehensive testing suite is provided in the `tests/` directory, validating the health check, mock authentication bypass rules, spatial boundaries, and the Safety Engine equations.

```bash
# Run all tests
make test
# Or directly
pytest
```

---

## 📖 API Documentation
Once the application server is active:
- **Swagger Interactive UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc alternative documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Service Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🔒 Security Design Core Rules
1. **No Coordinates in Logs:** Raw exact coordinates (latitude and longitude) are automatically stripped/redacted by custom log processors. Only H3 indexes or generalized bounding regions may be safely logged.
2. **Anonymized Audits:** Client IP addresses are securely hashed (SHA-256) prior to being recorded in the database `audit_logs` table.
3. **Privacy-Aggregated POIs & Incidents:** The `GET /safety/nearby` endpoint acts as a privacy guard, grouping precision coordinates into H3 grid aggregations to protect individuals reporting hazards or incidents.
