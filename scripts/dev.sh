#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "Applying database migrations..."
uv run python -m alembic upgrade head

echo "Starting development server..."
uv run python run.py
