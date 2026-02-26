#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ $# -lt 1 ]; then
  echo "Usage: scripts/makemigration.sh \"message\""
  exit 1
fi
uv run python -m alembic revision --autogenerate -m "$1"
