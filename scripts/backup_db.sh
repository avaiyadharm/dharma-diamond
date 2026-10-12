#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$ROOT_DIR/backups"
mkdir -p "$BACKUP_DIR"

if [[ -f "$ROOT_DIR/backend/.env" ]]; then
  set -a
  source "$ROOT_DIR/backend/.env"
  set +a
fi

STAMP="$(date +%Y%m%d-%H%M%S)"

if [[ "${DATABASE_URL:-}" == postgresql* ]]; then
  if ! command -v pg_dump >/dev/null 2>&1; then
    echo "pg_dump is required for PostgreSQL backups but is not installed." >&2
    exit 1
  fi
  TARGET="$BACKUP_DIR/dharma-diamond-${STAMP}.dump"
  pg_dump "$DATABASE_URL" --format=custom --file="$TARGET"
  echo "PostgreSQL backup saved to: $TARGET"
else
  TARGET="$BACKUP_DIR/dharma-diamond-${STAMP}.db"
  cp "$ROOT_DIR/dharma_diamond.db" "$TARGET"
  echo "SQLite backup saved to: $TARGET"
fi
