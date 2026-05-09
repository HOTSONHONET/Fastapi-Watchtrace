#!/usr/bin/env bash
set -euo pipefail

WHEEL_PATH="${1:-}"

if [[ -z "$WHEEL_PATH" ]]; then
  WHEEL_PATH="$(ls dist/*.whl | head -n 1)"
fi

if [[ ! -f "$WHEEL_PATH" ]]; then
  echo "Wheel not found: $WHEEL_PATH"
  exit 1
fi

TMP_DIR="$(mktemp -d)"
SERVER_PID=""

cleanup() {
  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

cd "$TMP_DIR"

uv init --bare
uv add fastapi uvicorn
uv add "$WHEEL_PATH"

cat > main.py <<'PY'
from fastapi import FastAPI
from watchtower import setup_watchtower

app = FastAPI()

setup_watchtower(
    app,
    source_root=".",
    code_index_path=".code_index.json",
    output_dir=".watchtower",
    enable_ui=True,
)

@app.get("/")
async def healthcheck():
    return {"status": "ok"}
PY

uv run uvicorn main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
SERVER_PID=$!

sleep 5
cat server.log

curl -fsS http://127.0.0.1:8000/ | grep -q "ok"
curl -fsS http://127.0.0.1:8000/__watchtower/ | grep -q '<div id="root"></div>'
curl -fsS http://127.0.0.1:8000/__watchtower/ | grep -q '/__watchtower/assets/'
curl -fsS http://127.0.0.1:8000/__watchtower/api/requests

echo "Wheel smoke test passed: $WHEEL_PATH"
