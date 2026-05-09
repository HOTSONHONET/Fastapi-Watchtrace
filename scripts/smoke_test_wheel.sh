#!/usr/bin/env bash
set -euo pipefail

WHEEL_PATH="${1:-}"

if [[ -z "$WHEEL_PATH" ]]; then
  mapfile -t WHEELS < <(ls dist/fastapi_watchtrace-*.whl 2>/dev/null || true)

  if [[ "${#WHEELS[@]}" -ne 1 ]]; then
    echo "Expected exactly one fastapi-watchtrace wheel, found ${#WHEELS[@]}"
    echo "Available wheels:"
    ls dist/*.whl 2>/dev/null || true
    exit 1
  fi

  WHEEL_PATH="${WHEELS[0]}"
fi

if [[ ! -f "$WHEEL_PATH" ]]; then
  echo "Wheel not found: $WHEEL_PATH"
  exit 1
fi

# Important: resolve wheel path before moving into temp dir
WHEEL_PATH="$(realpath "$WHEEL_PATH")"

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
from watchtrace import setup_watchtrace

app = FastAPI()

setup_watchtrace(
    app,
    source_root=".",
    code_index_path=".code_index.json",
    output_dir=".watchtrace",
    enable_ui=True,
)

@app.get("/")
async def healthcheck():
    return {"status": "ok"}
PY

uv run uvicorn main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
SERVER_PID=$!

# Wait until server is ready, max ~10 seconds
for i in {1..20}; do
  if curl -fsS http://127.0.0.1:8000/ >/dev/null 2>&1; then
    break
  fi

  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    echo "Server process exited early"
    cat server.log
    exit 1
  fi

  sleep 0.5
done

echo "----- server.log -----"
cat server.log
echo "----------------------"

curl -fsS http://127.0.0.1:8000/ | grep -q "ok"
curl -fsS http://127.0.0.1:8000/__watchtrace/ | grep -q '<div id="root"></div>'
curl -fsS http://127.0.0.1:8000/__watchtrace/ | grep -q '/__watchtrace/assets/'
curl -fsS http://127.0.0.1:8000/__watchtrace/api/requests

echo "Wheel smoke test passed: $WHEEL_PATH"