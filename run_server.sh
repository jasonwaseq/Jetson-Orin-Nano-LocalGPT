#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source ./config.env

cd ~/llama.cpp

if [ ! -f "$MODEL" ]; then
    echo "Error: Model file not found at $MODEL"
    exit 1
fi

if [ ! -x "./build/bin/llama-server" ]; then
    echo "Error: llama-server binary not found at ./build/bin/llama-server"
    exit 1
fi

exec ./build/bin/llama-server \
  -m "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  --ctx-size "$CTX" \
  --n-gpu-layers "$GPU_LAYERS"
