#!/bin/bash
set -e

# Usage: ./test-sql.sh <PORT> <TEST_WORD>
PORT=${1:-8005}
TEST_WORD=${2:-dev_db}

RESPONSE=$(curl -sSf -X POST http://localhost:$PORT/execute_sql \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM transactions LIMIT 1;"}')
echo "Response: $RESPONSE"
DESCRIPTION=$(echo "$RESPONSE" | jq -r '.result[0].Description')
if echo "$DESCRIPTION" | grep -q "$TEST_WORD"; then
  echo "Integration test passed."
else
  echo "Integration test failed. Description does not contain '$TEST_WORD'. Got: $DESCRIPTION" >&2
  exit 1
fi
