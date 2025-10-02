#!/usr/bin/env bash
set -e
# Simple wait for mongodb (optional)
if [ -n "$MONGO_URI" ]; then
  echo "MONGO_URI is set"
fi
exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload