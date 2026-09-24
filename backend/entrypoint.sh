#!/bin/sh
set -eu

MODEL_FILE="${MODEL_PATH:-/models/current/model.joblib}"
REGISTRY_DIR="$(dirname "$MODEL_FILE")"

if [ ! -f "$MODEL_FILE" ]; then
  echo "No model at $MODEL_FILE — training a local registry copy"
  python mlops/train.py --registry "$REGISTRY_DIR"
fi

exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
