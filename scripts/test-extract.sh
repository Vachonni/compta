#!/bin/bash
set -euo pipefail

## Purpose: Integration test for the /extract_file endpoint.
## It validates both accepted path forms when possible:
##   1) Absolute path inside the service blob root (as returned by /upload_file)
##   2) Absolute path starting with /blob/(dev|prod)/...
##
## Usage:
##   APP_ENV=dev ./scripts/test-extract.sh <ABS_OR_BLOB_PATH>
##   APP_ENV=dev ./scripts/test-extract.sh --path <ABS_OR_BLOB_PATH>
##
## Env vars (optional for dual-form testing):
##   LOCAL_DATABASES_DIR  Host blob root (so script can synthesize the absolute form if given /blob/...)
##   APP_ENV              dev|staging|prod|local (affects port + environment segment detection)
##
## Exit codes:
##   0 success; 2 usage error; 4 curl/HTTP error; 5 second-form synthesis failed (treated as warning unless primary fails)

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <ABS_OR_BLOB_PATH>" >&2
  echo "       $0 --path <ABS_OR_BLOB_PATH>" >&2
  exit 2
fi

if [[ $1 == "--path" ]]; then shift; fi
INPUT_PATH=$1

if [[ -z "$INPUT_PATH" ]]; then
  echo "Empty path argument." >&2
  exit 2
fi

APP_ENV_VAL=${APP_ENV:-dev}
case "$APP_ENV_VAL" in
  dev|DEV) PORT=8001 ; BUCKET=dev ;;
  staging|STAGING) PORT=8005 ; BUCKET=dev ;;
  prod|PROD|production|PRODUCTION) PORT=8009 ; BUCKET=prod ;;
  local|LOCAL) PORT=8000 ; BUCKET=dev ;;
  *) echo "Warning: unknown APP_ENV='$APP_ENV_VAL', defaulting to staging port 8005" >&2; PORT=8005; BUCKET=dev ;;
 esac

PRIMARY_PATH=""
ALTERNATE_PATH=""

if [[ "$INPUT_PATH" == /blob/* ]]; then
  # INPUT is blob form; keep as primary
  PRIMARY_PATH="$INPUT_PATH"
  # Try to synthesize absolute form if LOCAL_DATABASES_DIR available
  if [[ -n "${LOCAL_DATABASES_DIR:-}" ]]; then
    # Detect optional env segment
    if [[ "$INPUT_PATH" =~ ^/blob/(dev|prod)/(.+) ]]; then
      ENV_SEG=${BASH_REMATCH[1]}; REST=${BASH_REMATCH[2]}
    else
      # No env segment provided; infer from APP_ENV -> dev for non-prod
      if [[ $APP_ENV_VAL == prod* || $APP_ENV_VAL == PROD* ]]; then ENV_SEG=prod; else ENV_SEG=dev; fi
      REST=${INPUT_PATH#/blob/}
    fi
    ALTERNATE_PATH="${LOCAL_DATABASES_DIR%/}/blob/${ENV_SEG}/$REST"
  fi
else
  # INPUT assumed absolute path (inside blob root), use as primary
  PRIMARY_PATH="$INPUT_PATH"
  # Attempt to extract blob form
  if [[ "$INPUT_PATH" =~ (/blob/(dev|prod)/.+) ]]; then
    # Extract from first /blob/ occurrence, normalizing leading slash
    REL_WITH_BLOB=${BASH_REMATCH[1]}
    ALTERNATE_PATH="$REL_WITH_BLOB"
  fi
fi

echo "Primary extract path: $PRIMARY_PATH"
if [[ -n "$ALTERNATE_PATH" && "$ALTERNATE_PATH" != "$PRIMARY_PATH" ]]; then
  echo "Alternate extract path: $ALTERNATE_PATH"
else
  echo "Alternate path not derivable (will only test primary)." >&2
fi

# If primary is /blob form and we have a derived absolute alternate, perform a local existence hint.
if [[ "$PRIMARY_PATH" == /blob/* && -n "$ALTERNATE_PATH" && -f "$ALTERNATE_PATH" ]]; then
  echo "Verified host file exists at: $ALTERNATE_PATH"
elif [[ "$PRIMARY_PATH" == /blob/* && -n "$ALTERNATE_PATH" && ! -f "$ALTERNATE_PATH" ]]; then
  echo "Warning: Host file not found at derived absolute path: $ALTERNATE_PATH" >&2
  echo "If the API returns 404, ensure the file was uploaded (owner/year/month/bank) and that LOCAL_DATABASES_DIR matches the service mount." >&2
fi

run_extract() {
  local PATH_ARG=$1
  local LABEL=$2
  echo "--- Extracting ($LABEL) path=$PATH_ARG"
  local TMP_OUT
  TMP_OUT=$(mktemp /tmp/extracted_file.XXXXXX)
  set +e
  local HTTP_STATUS
  HTTP_STATUS=$(curl -sS -G "http://localhost:${PORT}/extract_file" --data-urlencode "path=${PATH_ARG}" -o "$TMP_OUT" -w "%{http_code}")
  local CURL_STATUS=$?
  set -e
  if [[ $CURL_STATUS -ne 0 ]]; then
    echo "Curl failed (exit $CURL_STATUS) for $LABEL." >&2
    rm -f "$TMP_OUT"
    return 4
  fi
  if [[ "$HTTP_STATUS" != "200" ]]; then
    echo "HTTP $HTTP_STATUS for $LABEL (expected 200)." >&2
    echo "Body:" >&2
    sed 's/^/  /' "$TMP_OUT" >&2 || true
    rm -f "$TMP_OUT"
    return 4
  fi
  local SIZE
  SIZE=$(wc -c < "$TMP_OUT" | tr -d ' ')
  echo "Extracted ($LABEL) size=${SIZE} bytes"
  if [[ $SIZE -gt 0 ]]; then
    if file "$TMP_OUT" | grep -qi 'text\|csv\|pdf'; then
      head -n 1 "$TMP_OUT" | sed 's/^/  preview: /'
    fi
  fi
  if [[ "${KEEP_TMP:-false}" != "true" ]]; then
    rm -f "$TMP_OUT" || true
  else
    echo "Kept temp file: $TMP_OUT"
  fi
  return 0
}

STATUS_PRIMARY=0
run_extract "$PRIMARY_PATH" primary || STATUS_PRIMARY=$?

STATUS_ALT=0
if [[ -n "$ALTERNATE_PATH" && "$ALTERNATE_PATH" != "$PRIMARY_PATH" ]]; then
  run_extract "$ALTERNATE_PATH" alternate || STATUS_ALT=$?
else
  echo "Skipping alternate extraction (not available)." >&2
fi

if [[ $STATUS_PRIMARY -ne 0 ]]; then
  echo "Primary extraction failed." >&2
  exit $STATUS_PRIMARY
fi
if [[ $STATUS_ALT -ne 0 ]]; then
  echo "Alternate extraction failed." >&2
  exit $STATUS_ALT
fi

echo "Both extraction forms succeeded.";
exit 0
