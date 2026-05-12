# Auto Recovery 문서

## 1. 문서 목적

본 문서는 `OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템` 프로젝트에서 Python 기반 자동 복구 스크립트를 구현하고 운영하는 방식을 정리한 문서이다.

Auto Recovery는 Health Checker가 감지한 비정상 VM 상태를 기반으로 복구 작업을 수행하고, 결과를 로그 및 Incident Report로 남긴다.

---

## 2. 구현 목표

자동 복구 기능의 목표는 다음과 같다.

- VM 비정상 상태 감지 결과 수신
- 장애 상태별 복구 방식 분기
- `SHUTOFF` 상태 VM 자동 시작
- 복구 후 상태 재확인
- 복구 성공/실패 로그 저장
- Incident Report 자동 생성

---

## 3. 동작 구조

```text
vm_health_checker.py
   ↓
비정상 VM 감지
   ↓
auto_recovery.py
   ↓
장애 유형 분류
   ↓
OpenStack CLI/API 복구 명령 실행
   ↓
상태 재확인
   ↓
recovery.log 기록
   ↓
incident_report.py
   ↓
Markdown 장애 보고서 생성
```

---

## 4. 주요 파일

```text
automation/
├── config.yaml
├── openstack_client.py
├── vm_health_checker.py
├── auto_recovery.py
└── incident_report.py
```

---

## 5. 설정 파일

`automation/config.yaml`

```yaml
openstack:
  openrc_path: "./demo-openrc"

health_check:
  expected_status: "ACTIVE"
  target_servers:
    - web-01
    - db-01
    - monitor-01
    - test-01

recovery:
  enabled: true
  wait_seconds: 10
  max_retry: 3

log:
  path: "./logs/vm-health-check.log"
  recovery_path: "./logs/recovery.log"

report:
  path: "./reports"
```

---

## 6. 복구 대상 상태

| 상태 | 자동 복구 여부 | 처리 방식 |
|---|---|---|
| ACTIVE | 복구 불필요 | 정상 상태 |
| SHUTOFF | 자동 복구 | `openstack server start` 실행 |
| ERROR | 수동 점검 | Incident Report 생성 |
| BUILD | 수동 점검 | 상태 확인 필요 |
| UNKNOWN | 수동 점검 | 원인 확인 필요 |

---

## 7. 자동 복구 흐름

## 7.1 SHUTOFF 상태 복구

VM 상태가 `SHUTOFF`이면 다음 명령어를 실행한다.

```bash
openstack server start <VM_NAME>
```

이후 설정된 간격으로 상태를 재확인한다.

```text
wait_seconds: 10
max_retry: 3
```

즉, 10초 간격으로 최대 3번 상태를 확인한다.

---

## 7.2 ERROR 상태 처리

VM 상태가 `ERROR`인 경우 자동으로 재시작하지 않고 수동 점검 대상으로 분류한다.

이유:

- 이미지 문제
- Nova Compute 문제
- 리소스 부족
- Hypervisor 문제
- 스토리지 연결 문제

등 다양한 원인이 있을 수 있기 때문이다.

따라서 `ERROR` 상태는 Incident Report를 생성하고 관리자가 원인을 분석하도록 한다.

---

## 8. 실행 방법

가상환경 활성화:

```bash
source .venv/bin/activate
```

VM 상태 감지 및 자동 복구 실행:

```bash
python automation/vm_health_checker.py
```

자동 복구만 단독 실행:

```bash
python automation/auto_recovery.py test-01 SHUTOFF
```

---

## 9. 장애 시나리오 테스트

## 9.1 test-01 VM 중지

```bash
source demo-openrc
openstack server stop test-01
```

상태 확인:

```bash
openstack server list
```

예상 상태:

```text
test-01 SHUTOFF
```

---

## 9.2 Health Checker 실행

```bash
python automation/vm_health_checker.py
```

예상 출력:

```text
[WARN] test-01 status: SHUTOFF, expected: ACTIVE
[ACTION_REQUIRED] test-01 needs recovery
[START] Recovery started. Target: test-01, detected_status: SHUTOFF
[ACTION] openstack server start test-01
[CHECK] test-01 status check 1/3: ACTIVE
[SUCCESS] test-01 recovered to ACTIVE
```

---

## 10. 로그 파일

Health Check 로그:

```text
logs/vm-health-check.log
```

Recovery 로그:

```text
logs/recovery.log
```

Recovery 로그 예시:

```text
[2026-05-12 11:30:10] [START] Recovery started. Target: test-01, detected_status: SHUTOFF
[2026-05-12 11:30:10] [ACTION] openstack server start test-01
[2026-05-12 11:30:20] [CHECK] test-01 status check 1/3: ACTIVE
[2026-05-12 11:30:20] [SUCCESS] test-01 recovered to ACTIVE
```

---

## 11. Incident Report

자동 복구 결과는 Markdown 보고서로 저장된다.

저장 위치:

```text
reports/
```

파일명 예시:

```text
incident-20260512-113010-test-01.md
```

보고서 포함 항목:

- 발생 시간
- 대상 서버
- 장애 유형
- 감지 상태
- 복구 작업
- 복구 결과
- 상세 로그
- 재발 방지 방안

---

## 12. README에 사용할 캡처 목록

| 파일명 | 캡처 내용 |
|---|---|
| `screenshots/auto-recovery-log.png` | 자동 복구 로그 |
| `screenshots/incident-report.png` | Incident Report 생성 결과 |
| `screenshots/vm-shutoff-before.png` | 복구 전 VM SHUTOFF 상태 |
| `screenshots/vm-active-after.png` | 복구 후 VM ACTIVE 상태 |

---

## 13. 완료 기준

다음 항목이 완료되면 Auto Recovery 구현 단계가 완료된 것으로 판단한다.

- `automation/auto_recovery.py` 작성 완료
- `automation/incident_report.py` 작성 완료
- `vm_health_checker.py`와 자동 복구 연동 완료
- SHUTOFF 상태 VM 자동 시작 가능
- 복구 후 ACTIVE 상태 재확인 가능
- `logs/recovery.log` 생성 확인
- `reports/incident-*.md` 생성 확인