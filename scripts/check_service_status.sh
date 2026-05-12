#!/bin/bash

# 서비스 상태 점검 스크립트
# 사용 예시:
# ./scripts/check_service_status.sh nginx

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
  echo "[ERROR] Service name is required."
  echo "Usage: ./scripts/check_service_status.sh <service_name>"
  exit 2
fi

echo "[INFO] Checking service status: ${SERVICE_NAME}"

if systemctl is-active --quiet "$SERVICE_NAME"; then
  echo "[OK] ${SERVICE_NAME} is running."
  exit 0
else
  echo "[WARN] ${SERVICE_NAME} is not running."
  echo "[ACTION_REQUIRED] Restart service."
  exit 1
fi