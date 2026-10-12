# Dharma Diamond

Dharma Diamond is a single-user inventory and sales platform for diamonds and jewellery. The application is designed for secure traceability, item-level inventory, and audited movement history.

## Architecture

- Frontend: React + TypeScript + Vite + Tailwind
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: SQLite for local development, PostgreSQL-ready for production
- Auth: single admin bootstrap with environment-controlled credentials
- Inventory model: explicit state machine plus movement ledger for every item change

## Local setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. pytest -q
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Required environment variables

The backend reads the following environment values:

- `SECRET_KEY`: long random secret key used for JWT signing
- `ADMIN_EMAIL`: bootstrap email for the single authorized admin
- `ADMIN_PASSWORD`: bootstrap password for the single authorized admin
- `ADMIN_FULL_NAME`: display name for the admin
- `DATABASE_URL`: database connection string

The default seeded config is for local development only. In production, set these values explicitly and do not commit credentials to version control.

## Inventory-state policy

The app uses an explicit lifecycle model for each physical item:

- AVAILABLE
- RESERVED
- SOLD
- RETURNED_PENDING_INSPECTION
- AVAILABLE_AFTER_INSPECTION
- DAMAGED
- LOST
- UNDER_REPAIR
- ARCHIVED

A transition is only valid when it is defined in the inventory-state rules in [backend/app/core/inventory.py](backend/app/core/inventory.py). The state change must be recorded in the stock movement ledger and should never be done with a free-form DB update.

## Database backup and restore

### Backup

For SQLite (local dev):

```bash
cp dharma_diamond.db dharma_diamond.backup.db
```

For PostgreSQL:

```bash
pg_dump -d dharma_diamond -f dharma_diamond.sql
```

### Restore

For SQLite:

```bash
cp dharma_diamond.backup.db dharma_diamond.db
```

For PostgreSQL:

```bash
psql -d dharma_diamond < dharma_diamond.sql
```

This repository is not a substitute for regular database backups. Always verify restored data before relying on a backup.

## Current implementation status

The repository currently includes:

- FastAPI backend with authentication routes
- SQLAlchemy database models for diamonds, jewellery, purchase, sales, inventory, parties, and audit records
- Protected admin route patterns with token validation
- Explicit inventory lifecycle rules and transition validation
- A working pytest suite for auth and inventory-state checks

The next implementation steps are the remaining transactional modules: purchases, receipts, sales, reservations, payments, invoices, and reporting filters.
