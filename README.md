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

### 3. Persistent PostgreSQL with Docker

This repository includes a PostgreSQL-backed development configuration that stores data in a named Docker volume so the database survives normal restarts and container recreation, while leaving the local SQLite workflow intact for quick development.

```bash
cp .env.example .env
# update the DB values and secrets in the root .env file

docker compose up -d db
```

The database volume is defined in [docker-compose.yml](docker-compose.yml) as `postgres_data`, which keeps database files under Docker-managed persistent storage instead of ephemeral container storage.

To start the backend against PostgreSQL in Docker:

```bash
docker compose up --build -d backend
```

The app waits for the database health check before accepting backend API traffic.

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

For PostgreSQL or Docker-managed database, use the included helper script:

```bash
chmod +x scripts/backup_db.sh
./scripts/backup_db.sh
```

This stores the backup under the `backups/` folder and keeps the timestamped filename.

### Restore

For SQLite:

```bash
cp dharma_diamond.backup.db dharma_diamond.db
```

For PostgreSQL or Docker-managed database:

```bash
chmod +x scripts/restore_db.sh
./scripts/restore_db.sh backups/dharma-diamond-20261012-120000.dump
```

This repository is not a substitute for regular database backups. Always verify restored data before relying on a backup.

### Important operational note

Do not run `docker compose down -v` during normal updates, because this removes the named Docker volume and can erase persisted business data.

Use normal restart commands instead:

```bash
docker compose stop
docker compose start
```

or:

```bash
docker compose up -d db
```

## Persistence and restart behavior

The application is designed to keep business records in a durable database rather than browser memory or JavaScript state. Important records such as diamonds, jewellery, sales, payments, and stock movements are stored in the SQL backend and remain available after:

- browser refresh
- logout/login
- backend restart
- machine restart
- normal Docker container restarts

The database is the single source of truth for all business data; the frontend pulls fresh values from the API rather than relying on local mock arrays or localStorage for business records.

## Current implementation status

The repository currently includes:

- FastAPI backend with authentication routes
- SQLAlchemy database models for diamonds, jewellery, purchase, sales, inventory, parties, and audit records
- Protected admin route patterns with token validation
- Explicit inventory lifecycle rules and transition validation
- A working pytest suite for auth and inventory-state checks

The next implementation steps are the remaining transactional modules: purchases, receipts, sales, reservations, payments, invoices, and reporting filters.
