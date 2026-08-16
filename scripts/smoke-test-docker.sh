#!/usr/bin/env bash
# End-to-end smoke test against the Docker image (mirrors scripts/smoke-test.sh, but exercises
# the container specifically: image builds, the app starts and migrates the DB on a mounted
# volume, serves real traffic, and — critically — the data survives a container restart against
# the same volume, which is the whole point of persisting to a volume in the first place.
# Usage: smoke-test-docker.sh <image-tag>
# Requires: docker, curl, jq.
set -euo pipefail

image="$1"
data_dir="$(mktemp -d)"
container=pointify-smoke-test

cleanup() {
  docker rm -f "$container" > /dev/null 2>&1 || true
  # The container runs as root, so files it wrote under $data_dir are root-owned on the host
  # too — harmless on a throwaway CI runner, but don't let a permission-denied rm here mask an
  # otherwise-passing test run.
  rm -rf "$data_dir" 2>/dev/null || true
}
trap cleanup EXIT

start_container() {
  docker run -d --name "$container" -p 8000:8000 -e SECRET_KEY=smoke-test-secret-key \
    -v "$data_dir:/data" "$image" > /dev/null
  for _ in $(seq 1 30); do
    code="$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/ || true)"
    [ "$code" != "000" ] && [ -n "$code" ] && return
    sleep 1
  done
  echo "Container did not become ready in time. Logs:" >&2
  docker logs "$container" >&2
  exit 1
}

stop_container() {
  docker stop "$container" > /dev/null
  docker rm "$container" > /dev/null
}

start_container

# SPA served at /, client route falls back to index.html
curl -sf http://localhost:8000/ | grep -q '<app-root'
test "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/themes)" = 200

# Register, log in, create a theme/subtheme/point, verify stats via the API.
# Note: `-o /dev/null` (curl's own flag), not `> /dev/null` (shell redirect) — the latter
# intermittently fails with exit 23 ("failed writing body") on git-bash's mingw64 curl build
# when this script is run locally on Windows instead of a CI runner.
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

# The DB must have landed on the mounted volume, not somewhere inside the (about to be
# discarded) container filesystem.
test -f "$data_dir/pointify.db"

# Restart against the SAME volume: the point must still be there — this is the actual
# persistence guarantee the volume mount exists to provide.
stop_container
start_container
curl -sf -o /dev/null -c "$cookie_jar" -b "$cookie_jar" -H 'Content-Type: application/json' \
  -d '{"username":"smoketest","password":"hunter22"}' http://localhost:8000/api/auth/login
curl -sf -b "$cookie_jar" "http://localhost:8000/api/themes/$theme_id" \
  | jq -e '.stats.total_points == 1' > /dev/null

rm -f "$cookie_jar"
echo "Docker smoke test passed."
