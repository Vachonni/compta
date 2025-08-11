#!/bin/bash
# Usage: ./health-check.sh <PORT>
PORT=${1:-8005}
for i in {1..10}; do
  if curl -sSf http://localhost:$PORT/healthz; then
    echo "API is up!"
    exit 0
  fi
  echo "Waiting for API... ($i)"
  sleep 5
done
echo "API did not become ready in time" >&2
exit 1
