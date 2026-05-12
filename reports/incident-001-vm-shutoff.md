# Incident 001 - VM 비정상 종료 자동 복구

## 1. 시나리오 개요

OpenStack VM이 비정상적으로 종료된 상황을 가정하고, Python Health Checker가 VM 상태를 감지한 뒤 자동 복구 스크립트를 통해 VM을 다시 시작하는 시나리오이다.

---

## 2. 장애 정보

| 항목 | 내용 |
|---|---|
| 장애 번호 | INCIDENT-001 |
| 장애 유형 | VM 비정상 종료 |
| 대상 VM | test-01 |
| 감지 상태 | SHUTOFF |
| 정상 상태 | ACTIVE |
| 감지 방식 | OpenStack CLI 기반 VM 상태 조회 |
| 복구 방식 | `openstack server start test-01` |

---

## 3. 장애 발생 명령어

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
test-01    SHUTOFF
```

---

## 4. 감지 명령어

```bash
python automation/vm_health_checker.py
```

예상 출력:

```text
[WARN] test-01 status: SHUTOFF, expected: ACTIVE
[ACTION_REQUIRED] test-01 needs recovery
```

---

## 5. 복구 절차

Health Checker가 자동 복구 기능을 호출한다.

```text
vm_health_checker.py
  → auto_recovery.py
  → openstack server start test-01
  → 상태 재확인
```

실제 복구 명령어:

```bash
openstack server start test-01
```

---

## 6. 복구 후 확인

```bash
openstack server list
```

예상 결과:

```text
test-01    ACTIVE
```

---

## 7. 로그 확인

```bash
cat logs/vm-health-check.log
cat logs/recovery.log
```

확인할 로그:

```text
[WARN] test-01 status: SHUTOFF, expected: ACTIVE
[ACTION] openstack server start test-01
[SUCCESS] test-01 recovered to ACTIVE
```

---

## 8. 원인 분석

VM이 SHUTOFF 상태가 된 원인은 운영자의 수동 종료 또는 인스턴스 내부 장애로 가정한다.

실제 운영 환경에서는 다음 항목을 추가로 확인해야 한다.

- Nova Compute 로그
- Hypervisor 리소스 상태
- 인스턴스 이벤트 로그
- 호스트 재부팅 여부
- 사용자의 수동 종료 여부

---

## 9. 재발 방지

- VM 상태 주기 점검 자동화
- SHUTOFF 상태 감지 시 즉시 알림
- 반복 종료 VM에 대한 이벤트 로그 분석
- 중요 서비스 VM에 대한 재시작 정책 검토
