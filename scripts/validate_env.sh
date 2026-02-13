#!/usr/bin/env bash
# Simple env validator: checks required POSTGRES_* variables are present
set -eu
ENV_FILE=${1:-.env}
if [[ -f "$ENV_FILE" ]]; then
  source "$ENV_FILE"
fi

missing=()
for var in POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB POSTGRES_HOST POSTGRES_PORT; do
  if [[ -z "${!var:-}" ]]; then
    missing+=("$var")
  fi
done

if [ ${#missing[@]} -ne 0 ]; then
  echo "Missing required env vars: ${missing[*]}"
  exit 1
fi

echo "All required POSTGRES_* env vars are present."
