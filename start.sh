#!/bin/bash
# ============================================================
#  start.sh  –  Clean start for RAG Project
#  Kills existing servers, installs deps, starts both services
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "============================================================"
echo "  RAG Project – Clean Start"
echo "============================================================"

# ── 1. Kill anything running on port 8000 (API) or 3000 (frontend)
echo ""
echo "▶  Clearing ports 8000 and 3000..."
lsof -ti :8000 | xargs kill -9 2>/dev/null && echo "   ✓ Killed process on :8000" || echo "   ✓ Port 8000 already free"
lsof -ti :3000 | xargs kill -9 2>/dev/null && echo "   ✓ Killed process on :3000" || echo "   ✓ Port 3000 already free"
sleep 1

# ── 2. Activate virtual environment
echo ""
echo "▶  Activating virtual environment..."
source "$PROJECT_DIR/venv/bin/activate"

# ── 3. Install / upgrade missing Python packages silently
echo ""
echo "▶  Installing dependencies..."
pip install -q fastapi uvicorn python-multipart google-genai
echo "   ✓ Dependencies ready"

# ── 4. Start the FastAPI backend in the background
echo ""
echo "▶  Starting FastAPI backend on http://localhost:8000 ..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/rag_api.log 2>&1 &
API_PID=$!
echo "   ✓ API started (PID $API_PID)"
echo "   Logs: /tmp/rag_api.log"

# Give the API a moment to boot
sleep 3

# ── 5. Start the static frontend server in the background
echo ""
echo "▶  Starting Frontend on http://localhost:3000 ..."
python3 -m http.server 3000 --directory "$PROJECT_DIR/frontend" > /tmp/rag_frontend.log 2>&1 &
FE_PID=$!
echo "   ✓ Frontend started (PID $FE_PID)"

# ── 6. Done – open browser and show summary
echo ""
echo "============================================================"
echo "  🚀 Both services running!"
echo ""
echo "  API       → http://localhost:8000"
echo "  API Docs  → http://localhost:8000/docs"
echo "  Frontend  → http://localhost:3000"
echo ""
echo "  Press Ctrl+C to stop both."
echo "============================================================"
echo ""

# Open frontend in the default browser (macOS)
open http://localhost:3000 2>/dev/null || true

# ── 7. Tail both logs so output is visible; Ctrl+C kills both children
trap "echo ''; echo 'Shutting down...'; kill $API_PID $FE_PID 2>/dev/null; exit 0" INT TERM

# Follow API logs live (frontend server is mostly silent)
tail -f /tmp/rag_api.log
