# VM Health Checker 문서

## 1. 문서 목적

본 문서는 `OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템` 프로젝트에서 Python 기반으로 OpenStack VM 상태를 점검하는 Health Checker 구현 방식을 정리한 문서이다.

VM Health Checker는 OpenStack VM 상태를 주기적으로 확인하고, 비정상 상태를 감지하여 로그로 기록한다.

---

## 2. 구현 목표

VM Health Checker의 목표는 다음과 같다.

- OpenStack VM 목록 조회
- 관리 대상 VM 상태 확인
- 정상 상태와 비정상 상태 구분
- 비정상 VM 로그 기록
- 자동 복구 스크립트와 연계 가능한 구조 설계

---

## 3. 동작 구조

```text
config.yaml
   ↓
vm_health_checker.py
   ↓
openstack_client.py
   ↓
OpenStack CLI
   ↓
OpenStack API
   ↓
VM 상태 조회
   ↓
정상/비정상 판단
   ↓
로그 기록
```

---

## 4. 주요 파일

```text
automation/
├── config.yaml
├── openstack_client.py
└── vm_health_checker.py
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
  enabled: false

log:
  path: "./logs/vm-health-check.log"
```

설정 항목 설명:

| 항목 | 설명 |
|---|---|
| `openrc_path` | OpenStack 인증 정보가 포함된 openrc 파일 경로 |
| `expected_status` | 정상으로 판단할 VM 상태 |
| `target_servers` | 상태 점검 대상 VM 목록 |
| `recovery.enabled` | 자동 복구 활성화 여부 |
| `log.path` | Health Check 로그 저장 위치 |

---

## 6. OpenStack Client

`openstack_client.py`는 Python에서 OpenStack CLI 명령어를 실행하는 역할을 한다.

주요 기능:

| 함수 | 설명 |
|---|---|
| `list_servers()` | VM 목록 조회 |
| `get_server()` | 특정 VM 상세 조회 |
| `start_server()` | VM 시작 |
| `stop_server()` | VM 중지 |

OpenStack CLI 호출 예시:

```bash
source demo-openrc && openstack server list -f json
```

Python에서는 위 명령을 `subprocess`로 실행하고 JSON 결과를 파싱한다.

---

## 7. Health Check 판단 기준

본 프로젝트에서는 VM 상태가 `ACTIVE`이면 정상으로 판단한다.

| VM 상태 | 판단 |
|---|---|
| ACTIVE | 정상 |
| SHUTOFF | 비정상 |
| ERROR | 비정상 |
| BUILD | 확인 필요 |
| UNKNOWN | 비정상 |

---

## 8. 실행 방법

가상환경 생성:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

패키지 설치:

```bash
pip install pyyaml
```

실행:

```bash
python automation/vm_health_checker.py
```

특정 설정 파일을 지정해서 실행:

```bash
python automation/vm_health_checker.py automation/config.yaml
```

---

## 9. 실행 결과 예시

정상 상황:

```text
[2026-05-12 11:30:10] Starting VM health check
[2026-05-12 11:30:10] [OK] web-01 status: ACTIVE
[2026-05-12 11:30:10] [OK] db-01 status: ACTIVE
[2026-05-12 11:30:10] [OK] monitor-01 status: ACTIVE
[2026-05-12 11:30:10] [OK] test-01 status: ACTIVE
[2026-05-12 11:30:10] Finished VM health check
```

비정상 상황:

```text
[2026-05-12 11:35:22] Starting VM health check
[2026-05-12 11:35:22] [OK] web-01 status: ACTIVE
[2026-05-12 11:35:22] [OK] db-01 status: ACTIVE
[2026-05-12 11:35:22] [OK] monitor-01 status: ACTIVE
[2026-05-12 11:35:22] [WARN] test-01 status: SHUTOFF, expected: ACTIVE
[2026-05-12 11:35:22] [ACTION_REQUIRED] test-01 needs recovery
[2026-05-12 11:35:22] Finished VM health check
```

---

## 10. 로그 파일

로그는 다음 경로에 저장된다.

```text
logs/vm-health-check.log
```

로그 예시:

```text
[2026-05-12 11:35:22] [WARN] test-01 status: SHUTOFF, expected: ACTIVE
[2026-05-12 11:35:22] [ACTION_REQUIRED] test-01 needs recovery
```

---

## 11. 장애 시나리오 연계

VM 비정상 종료 시나리오:

```bash
openstack server stop test-01
```

Health Checker 실행:

```bash
python automation/vm_health_checker.py
```

예상 감지 결과:

```text
[WARN] test-01 status: SHUTOFF, expected: ACTIVE
[ACTION_REQUIRED] test-01 needs recovery
```

---

## 12. 자동 복구 연계 방향

현재 단계에서는 비정상 상태를 감지만 수행한다.

다음 단계에서는 `auto_recovery.py`를 연동하여 다음 동작을 수행한다.

```text
VM 상태 감지
   ↓
SHUTOFF 상태 확인
   ↓
auto_recovery.py 호출
   ↓
openstack server start <VM_NAME>
   ↓
복구 후 상태 재확인
```

---

## 13. 완료 기준

다음 항목이 완료되면 VM Health Checker 구현 단계가 완료된 것으로 판단한다.

- `automation/config.yaml` 작성 완료
- `automation/openstack_client.py` 작성 완료
- `automation/vm_health_checker.py` 작성 완료
- OpenStack VM 목록 조회 가능
- 정상 VM과 비정상 VM 구분 가능
- 로그 파일 생성 확인
- 장애 시나리오와 연계 가능