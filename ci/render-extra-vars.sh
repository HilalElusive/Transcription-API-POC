#!/usr/bin/env bash
set -euo pipefail

cat <<EOF
openai_api_key: "${OPENAI_API_KEY}"
openai_model: "gpt-4o-mini"
log_level: "INFO"
aws_region: "${AWS_DEFAULT_REGION}"
postgres_user: "transcription"
postgres_password: "${POSTGRES_PASSWORD}"
postgres_db: "transcription"
grafana_user: "admin"
grafana_password: "${GRAFANA_PASSWORD}"
api_image: "${IMAGE_NAME}:${IMAGE_TAG}"
EOF