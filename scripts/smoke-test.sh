#!/usr/bin/env bash
# End-to-end smoke test against a built Pointify app.
# Usage: smoke-test.sh <backend-dir>   (dir containing app/, with app/static/index.html
# already populated by copying the Angular build there)
# Starts the app on http://localhost:8000 with a fresh database, asserts SPA hosting +
# register/login/theme/subtheme/point + client-route fallback, restarts it to verify the
# data survives (same sqlite file on disk), then stops it.
# Requires: curl, jq, python3 (with the backend's deps installed and importable).
# Used by .github/workflows/smoke-ci.yml.
set -euo pipefail

app_dir="$1"

cd "$app_dir"
# Relative, deliberately — an absolute path built from `pwd` here would be MSYS/git-bash's
# POSIX-style rendering of the Windows path (e.g. /c/Users/...) on a Windows dev machine,
# which native Windows Python can't resolve and silently hangs on rather than erroring.
db_path="./pointify-smoketest.db"
rm -f "$db_path" "$db_path-shm" "$db_path-wal"
export DATABASE_URL="sqlite:///$db_path"
export SECRET_KEY="smoke-test-secret-key"
export ENVIRONMENT="production"

start_app() {
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
  app_pid=$!
  for _ in $(seq 1 30); do
    code="$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/ || true)"
    [ "$code" != "000" ] && [ -n "$code" ] && return
    sleep 1
  done
  echo "App did not become ready in time." >&2
  exit 1
}

stop_app() {
  kill "$app_pid" 2>/dev/null || true
  wait "$app_pid" 2>/dev/null || true
}
trap stop_app EXIT

start_app

# SPA served at /, client route falls back to index.html, favicon present.
# Note: `-o /dev/null` (curl's own flag), not `> /dev/null` (shell redirect) — the latter
# intermittently fails with exit 23 ("failed writing body") on git-bash's mingw64 curl build.
curl -sf http://localhost:8000/ | grep -q '<app-root'
test "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/themes)" = 200
curl -sf -o /dev/null http://localhost:8000/favicon.ico

# Register, log in, create a theme/subtheme/point, verify stats via the API
cookie_jar="$(mktemp)"
curl -sf -o /dev/null -c "$cookie_jar" -H 'Content-Type: application/json' \
  -d '{"username":"smoketest","password":"hunter22"}' http://localhost:8000/api/auth/register
curl -sf -o /dev/null -c "$cookie_jar" -b "$cookie_jar" -H 'Content-Type: application/json' \
  -d '{"username":"smoketest","password":"hunter22"}' http://localhost:8000/api/auth/login

theme_id="$(curl -sf -b "$cookie_jar" -H 'Content-Type: application/json' \
  -d '{"title":"Smoke theme"}' http://localhost:8000/api/themes | jq -r '.id')"
subtheme_id="$(curl -sf -b "$cookie_jar" -H 'Content-Type: application/json' \
  -d '{"title":"Smoke subtheme"}' "http://localhost:8000/api/themes/$theme_id/subthemes" | jq -r '.id')"
curl -sf -o /dev/null -b "$cookie_jar" -H 'Content-Type: application/json' \
  -d '{"type":"pro","text":"Works","rating":5}' "http://localhost:8000/api/subthemes/$subtheme_id/points"

curl -sf -b "$cookie_jar" "http://localhost:8000/api/themes/$theme_id" \
  | jq -e '.stats.total_points == 1' > /dev/null

# Restart: the sqlite file is on disk, so the point must still be there afterwards.
stop_app
start_app
curl -sf -o /dev/null -c "$cookie_jar" -b "$cookie_jar" -H 'Content-Type: application/json' \
  -d '{"username":"smoketest","password":"hunter22"}' http://localhost:8000/api/auth/login
curl -sf -b "$cookie_jar" "http://localhost:8000/api/themes/$theme_id" \
  | jq -e '.stats.total_points == 1' > /dev/null

rm -f "$cookie_jar"
echo "Smoke test passed."
