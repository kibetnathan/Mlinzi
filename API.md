# Overview
A FastAPI application called "Mlinzi Fraud Detection" that serves flagged fraud transactions from a PostgreSQL database. It uses SQLModel (Pydantic + SQLAlchemy) for ORM/models and Alembic for migrations.

## Architecture

```
backend/api/app/
├── main.py                          # Entry point, creates the app
├── application/app.py               # App factory (FastAPI instance)
├── database.py                      # PostgreSQL engine + session (get_db)
├── models/
│   ├── transactions.py              # Transaction SQLModel (table + schemas)
│   └── user.py                      # User SQLModel (not wired up yet)
├── routes/
│   ├── transactions.py              # Transaction endpoints
│   └── user.py                      # User endpoints (stub)
└── services/
    └── transactions.py              # Business logic for querying/ingesting flagged txns
```
# Features
1. Transaction Flagging API
Two endpoints under /transactions:
- GET /transactions/flagged — Returns all flagged transactions for a given date, optionally filtered by ?flag=velocity or ?flag=repeated. Defaults to today's date.
- GET /transactions/flagged/{flag} — Same but with the flag type in the path.
2. Lazy CSV Seeding
When no flagged transactions exist in the DB for a date, the service (services/transactions.py:46) automatically loads the CSV from data/mlinzi_sample_transactions.csv, runs both fraud detection modules:
- Velocity detection (velocity_detection/velocity.py)
- Repeated withdrawal detection (repeated_withdrawal/repeated.py)
It merges results (a transaction flagged by both gets flag: "velocity,repeated"), deduplicates against existing DB records, and bulk-inserts.
3. User Model
models/user.py defines a User table with id (UUID), username, email, display_name, and password_hash. The /users/ route exists but is a stub ("not ready").
4. Database & Migrations
- PostgreSQL 16 via docker-compose.yaml
- Alembic migrations with 6 versions tracking schema evolution (create tables → add is_flagged/flags → add reason/severity → remove severity)
- DB URL from DATABASE_URL env var, defaults to localhost:5432
How to Use
### Start the DB
cd backend/api && docker-compose up -d

### Run the API (with uvicorn)
uvicorn app.main:app --reload --app-dir backend/api

### Query flagged transactions for today
curl http://localhost:8000/transactions/flagged

### Query velocity-flagged transactions for a specific date
curl "http://localhost:8000/transactions/flagged?flag=velocity&target_date=2025-07-20"

### Or via path param
curl http://localhost:8000/transactions/flagged/repeated
The first request auto-seeds the DB from the CSV if empty, so no manual migration seed step is needed.
