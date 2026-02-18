#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source ./config.env

# Pre-flight checks
command -v python3 >/dev/null 2>&1 || { echo >&2 "[!] python3 is required but not installed. Aborting."; exit 1; }
command -v curl >/dev/null 2>&1 || { echo >&2 "[!] curl is required but not installed. Aborting."; exit 1; }

# Check for python dependencies
if ! python3 -c "import rich" &> /dev/null; then
    echo "[!] Python dependency 'rich' not found. Please run: pip3 install -r requirements.txt"
    exit 1
fi

# Check for log file writability
if [ -f "server.log" ] && [ ! -w "server.log" ]; then
    echo "[!] server.log is not writable. Check permissions."
    exit 1
fi

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
