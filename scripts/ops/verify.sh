#!/usr/bin/env bash
set -e

# Move to root
cd "$(dirname "$0")/../.."

# 1. Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' not found. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 2. Sync dependencies and ensure venv exists
echo "🔄 Syncing virtual environment..."
uv sync --quiet

# 3. Run the diagnostic script (Updated name to check_env.py)
echo "🔍 Launching Diagnostic Suite..."
uv run --env-file .env python scripts/ops/check_env.py