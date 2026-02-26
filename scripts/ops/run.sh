#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "Starting backend (src-layout)..."
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --app-dir src --reload