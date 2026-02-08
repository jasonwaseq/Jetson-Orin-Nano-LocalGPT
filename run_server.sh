#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source ./config.env

cd ~/llama.cpp

exec ./build/bin/llama-server \
  -m "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  --ctx-size "$CTX" \
  --n-gpu-layers "$GPU_LAYERS"
