#!/bin/bash

# 디스크 사용량 점검 스크립트
# 사용 예시:
# ./scripts/check_disk_usage.sh
# ./scripts/check_disk_usage.sh 80

THRESHOLD=${1:-80}

echo "[INFO] Disk usage threshold: ${THRESHOLD}%"
echo "[INFO] Checking root filesystem usage..."

USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')

echo "[INFO] Current disk usage: ${USAGE}%"

if [ "$USAGE" -ge "$THRESHOLD" ]; then
  echo "[WARN] Disk usage is above threshold."
  echo "[ACTION_REQUIRED] Cleanup required."
  exit 1
else
  echo "[OK] Disk usage is normal."
  exit 0
fi