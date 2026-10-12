#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_FILE="${1:-}"

if [[ -z "$TARGET_FILE" ]]; then
  echo "Usage: $0 <backup-file>"
  echo "Example: $0 backups/dharma-diamond-20261012-120000.dump"
  exit 1
fi

if [[ ! -f "$ROOT_DIR/$TARGET_FILE" ]]; then
  echo "Backup file not found: $ROOT_DIR/$TARGET_FILE"
  exit 1
fi

if [[ "$TARGET_FILE" == *.dump ]]; then
  if [[ -f "$ROOT_DIR/backend/.env" ]]; then
    set -a
    source "$ROOT_DIR/backend/.env"
    set +a
  fi

  if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "DATABASE_URL is not set. Set it in backend/.env before restoring a PostgreSQL backup." >&2
    exit 1
  fi

  if ! command -v pg_restore >/dev/null 2>&1; then
    echo "pg_restore is required for PostgreSQL restore but is not installed." >&2
    exit 1
  fi

  pg_restore --clean --if-exists --no-owner --no-privileges -d "$DATABASE_URL" "$ROOT_DIR/$TARGET_FILE"
  echo "PostgreSQL restore complete from: $ROOT_DIR/$TARGET_FILE"
else
  cp "$ROOT_DIR/$TARGET_FILE" "$ROOT_DIR/dharma_diamond.db"
  echo "SQLite restore complete from: $ROOT_DIR/$TARGET_FILE"
fi
