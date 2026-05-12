#!/bin/bash

# 서비스 재시작 스크립트
# 사용 예시:
# ./scripts/restart_service.sh nginx

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
  echo "[ERROR] Service name is required."
  echo "Usage: ./scripts/restart_service.sh <service_name>"
  exit 2
fi

echo "[ACTION] Restarting service: ${SERVICE_NAME}"

sudo systemctl restart "$SERVICE_NAME"

if systemctl is-active --quiet "$SERVICE_NAME"; then
  echo "[SUCCESS] ${SERVICE_NAME} restarted successfully."
  exit 0
else
  echo "[FAILED] Failed to restart ${SERVICE_NAME}."
  exit 1
fi