# Incident 003 - 디스크 사용량 초과 감지 및 정리

## 1. 시나리오 개요

test-01 VM에서 대용량 dummy 파일을 생성하여 디스크 사용량이 임계치를 초과한 상황을 가정하고, 디스크 점검 스크립트로 감지한 뒤 불필요한 파일을 제거하는 시나리오이다.

---

## 2. 장애 정보

| 항목 | 내용 |
|---|---|
| 장애 번호 | INCIDENT-003 |
| 장애 유형 | Disk Usage High |
| 대상 VM | test-01 |
| 감지 기준 | Disk usage 80% 이상 |
| 감지 방식 | `df` 명령어 기반 점검 |
| 복구 방식 | 임시 파일 및 로그 정리 |

---

## 3. 장애 발생 명령어

test-01에서 실행:

```bash
fallocate -l 2G /tmp/dummy-file
```

디스크 사용량 확인:

```bash
df -h
```

---

## 4. 감지 명령어

```bash
./scripts/check_disk_usage.sh 80
```

예상 출력:

```text
[WARN] Disk usage is above threshold.
[ACTION_REQUIRED] Cleanup required.
```

---

## 5. 복구 명령어

dummy 파일 삭제:

```bash
rm -f /tmp/dummy-file
```

로그 파일 정리 예시:

```bash
sudo journalctl --vacuum-time=3d
```

APT 캐시 정리:

```bash
sudo apt clean
```

---

## 6. 복구 후 확인

```bash
df -h
./scripts/check_disk_usage.sh 80
```

예상 출력:

```text
[OK] Disk usage is normal.
```

---

## 7. 원인 분석

디스크 사용량 초과는 다음 원인으로 발생할 수 있다.

- 로그 파일 누적
- 임시 파일 미정리
- 백업 파일 누적
- 애플리케이션 업로드 파일 증가
- 패키지 캐시 증가

---

## 8. 재발 방지

- 로그 로테이션 설정
- 디스크 사용량 모니터링
- 임계치 초과 시 알림 설정
- 불필요한 임시 파일 주기 정리
- 서비스별 데이터 저장 위치 분리
