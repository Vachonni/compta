#!/bin/bash
set -e

# Usage:
#   Port is derived from APP_ENV, do not pass it:
#     ./scripts/test-upload.sh <OWNER> <YEAR> <MONTH> <BANK> <FILE_PATH> [overwrite]
# Example:
#   APP_ENV=staging ./scripts/test-upload.sh G 2025 8 BNP /path/to/statement.pdf false
#   APP_ENV=dev     ./scripts/test-upload.sh G 2025 8 BNP /path/to/statement.pdf
#
# Env vars:
#   LOCAL_DATABASES_DIR  If set, script verifies (and can delete) the saved file on host.
#   APP_ENV              Controls bucket resolution (prod -> prod, otherwise dev). Optional.
#   CLEANUP              If set to 'true', remove the uploaded test file after verification.

# Parse args (no port expected)
if [[ $# -ge 5 ]]; then
  OWNER=$1; YEAR=$2; MONTH=$3; BANK=$4; FILE_PATH=$5; OVERWRITE=${6:-false}
else
  echo "Usage: $0 <OWNER> <YEAR> <MONTH> <BANK> <FILE_PATH> [overwrite]" >&2
  exit 2
fi

# Determine port from APP_ENV
APP_ENV_VAL=${APP_ENV:-dev}
case "$APP_ENV_VAL" in
  dev|DEV) PORT=8001 ; BUCKET=dev ;;
  staging|STAGING) PORT=8005 ; BUCKET=dev ;;
  prod|PROD|production|PRODUCTION) PORT=8009 ; BUCKET=prod ;;
  local|LOCAL) PORT=8000 ; BUCKET=dev ;;
  *) echo "Warning: unknown APP_ENV='$APP_ENV_VAL', defaulting to staging port 8005" >&2; PORT=8005; BUCKET=dev ;;
esac

if [[ ! -f "$FILE_PATH" ]]; then
  echo "File not found: $FILE_PATH" >&2
  exit 3
fi

echo "Uploading file to http://localhost:${PORT}/upload_file"
echo "  env=${APP_ENV_VAL} owner=${OWNER} year=${YEAR} month=${MONTH} bank=${BANK} overwrite=${OVERWRITE}"

# Perform upload (curl will fail for non-2xx due to -f; set -e will exit script)
RESPONSE=$(curl -sSf -X POST "http://localhost:${PORT}/upload_file" \
  -F "owner=${OWNER}" \
  -F "year=${YEAR}" \
  -F "month=${MONTH}" \
  -F "bank=${BANK}" \
  -F "file=@${FILE_PATH}" \
  -F "overwrite=${OVERWRITE}")

echo "Response: $RESPONSE"

DETAIL=$(echo "$RESPONSE" | jq -r '.detail // empty' 2>/dev/null || true)

if [[ "$DETAIL" == "File uploaded successfully." ]]; then
  echo "Upload passed."
  # Optional verification on host filesystem if LOCAL_DATABASES_DIR is provided
  if [[ -n "${LOCAL_DATABASES_DIR:-}" ]]; then
    EXT=${FILE_PATH##*.}
    EXT_LOWER=$(printf "%s" "$EXT" | tr '[:upper:]' '[:lower:]')
  TARGET_PATH="$LOCAL_DATABASES_DIR/blob/${BUCKET}/raw/${YEAR}/${MONTH}/${OWNER}_${BANK}.${EXT_LOWER}"
    if [[ -f "$TARGET_PATH" ]]; then
      echo "Verified file exists at: $TARGET_PATH"
      if [[ "${CLEANUP:-false}" == "true" ]]; then
        rm -f "$TARGET_PATH" || true
        if [[ ! -f "$TARGET_PATH" ]]; then
          echo "Cleaned up test artifact: $TARGET_PATH"
        else
          echo "Warning: failed to remove test artifact: $TARGET_PATH" >&2
        fi
      fi
    else
      echo "Warning: Expected file not found at: $TARGET_PATH" >&2
    fi
  fi
  exit 0
else
  echo "Upload failed. Detail: ${DETAIL:-unknown}. Full response above." >&2
  exit 1
fi
