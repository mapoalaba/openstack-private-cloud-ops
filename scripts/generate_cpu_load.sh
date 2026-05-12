#!/bin/bash

# CPU 부하 생성 스크립트
# 사용 예시:
# ./scripts/generate_cpu_load.sh
# ./scripts/generate_cpu_load.sh 2 120

CPU_WORKERS=${1:-2}
TIMEOUT=${2:-120}

echo "[INFO] Generating CPU load..."
echo "[INFO] CPU workers: ${CPU_WORKERS}"
echo "[INFO] Timeout: ${TIMEOUT} seconds"

if ! command -v stress >/dev/null 2>&1; then
  echo "[INFO] stress is not installed. Installing..."
  sudo apt update
  sudo apt install -y stress
fi

stress --cpu "$CPU_WORKERS" --timeout "$TIMEOUT"

echo "[INFO] CPU load test finished."