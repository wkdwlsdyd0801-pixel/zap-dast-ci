#!/usr/bin/env bash
# Run the OWASP ZAP baseline scan locally against the demo app, the same way
# CI does. Requires Docker. Produces zap-report.html in the current directory.
set -euo pipefail

NET=zap-dast-net
APP=zap-dast-app
TARGET="http://${APP}:5000"

cleanup() {
  # Always tear the target and network down, even if the scan fails.
  docker rm -f "${APP}" >/dev/null 2>&1 || true
  docker network rm "${NET}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# A user-defined network lets the scanner container resolve the app by name.
docker network create "${NET}" >/dev/null
docker build -t "${APP}:local" .
docker run -d --rm --name "${APP}" --network "${NET}" "${APP}:local" >/dev/null

# Wait until the app answers its health probe before scanning, so ZAP does not
# scan a half-booted process and report false "connection refused" results.
for _ in $(seq 1 30); do
  if docker run --rm --network "${NET}" curlimages/curl:8.10.1 \
        -fsS "${TARGET}/healthz" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

# zap-baseline.py is a passive-only spider+scan: safe, fast, no attack payloads.
# -I keeps the exit code 0 on WARN so local runs are not blocked; the rules
# file decides what counts as a hard FAIL. Mount cwd so the report lands here.
docker run --rm --network "${NET}" -v "$(pwd):/zap/wrk:rw" \
  ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t "${TARGET}/" \
  -c rules.tsv \
  -r zap-report.html \
  -I

echo "Report written to zap-report.html"
