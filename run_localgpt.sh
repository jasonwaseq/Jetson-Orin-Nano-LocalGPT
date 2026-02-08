#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source ./config.env

# Start server if not listening
if ! ss -lnt | grep -q ":${PORT}"; then
  echo "[+] starting llama-server on ${HOST}:${PORT}"
  nohup ./run_server.sh > server.log 2>&1 &
fi

# Wait until server is actually ready (up to ~60s)
echo "[+] waiting for server to become ready..."
for i in $(seq 1 60); do
  if curl -s --compressed "http://${HOST}:${PORT}/" >/dev/null 2>&1; then
    echo "[+] server is ready"
    break
  fi
  sleep 1
  if [ "$i" -eq 60 ]; then
    echo "[!] server did not become ready. Showing last logs:"
    tail -n 60 server.log || true
    exit 1
  fi
done

echo "[+] launching LocalGPT CLI"
HOST="$HOST" PORT="$PORT" ./localgpt.py
