#!/usr/bin/env bash
set -euo pipefail

# Navigate to project root
cd "$(dirname "$0")/../.."

clear
echo "🛡️  AAA-BACKEND SYSTEMATIC GUARD"
echo "------------------------------------------------------------"

# Run diagnostic script and capture token
# We redirect stderr to null to keep the TOKEN capture clean
DIAG_OUTPUT=$(uv run --env-file .env python scripts/ops/check_env.py --token 2>/dev/null || echo "FAILED")

if [[ "$DIAG_OUTPUT" == "FAILED" ]]; then
    echo "❌ Critical environment failure."
    exit 1
fi

# Extract token using sed
TOKEN=$(echo "$DIAG_OUTPUT" | sed -n 's/.*TOKEN_START:\(.*\):TOKEN_END.*/\1/p')

# Display diagnostic logs but hide the raw TOKEN_START line
echo "$DIAG_OUTPUT" | grep -v "TOKEN_START"

# Ghost Check: Clean up port 8080
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

echo "------------------------------------------------------------"
echo "🔡 CHEAT SHEET"
echo "   Endpoint : http://localhost:8080/api/dining-rooms/"
[[ -n "$TOKEN" ]] && echo "   Token    : Generated (Ready for curl)" || echo "   Token    : ❌ Check check_env.py"

if [[ -n "$TOKEN" ]]; then
    echo "📡 AUTH SMOKE TEST..."
    # Quick HEAD request to check if server is already responsive (or just check path)
    curl -I -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/auth/me | grep "HTTP" || echo "   ℹ️ Server offline (Ready to boot)"
fi
echo "------------------------------------------------------------"

read -p "🚀 Start Server? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    uv run python run.py
fi