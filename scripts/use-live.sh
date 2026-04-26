#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_FILE="${ROOT_DIR}/backend/.env.live.example"
DST_FILE="${ROOT_DIR}/backend/.env"

if [[ ! -f "${SRC_FILE}" ]]; then
  echo "Missing source file: ${SRC_FILE}" >&2
  exit 1
fi

cp "${SRC_FILE}" "${DST_FILE}"
echo "Switched to LIVE mode env template."
echo "Updated: ${DST_FILE}"
echo "Important: set OPENAI_API_KEY in backend/.env before starting backend."
echo "Next: restart backend server."
