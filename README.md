# OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템

## 1. 프로젝트 개요

본 프로젝트는 신입 Cloud Engineer 직무에서 요구되는 Linux 서버 운영, OpenStack 기반 Private Cloud 구축, VM/Network/Storage/User 관리, 모니터링, 장애 대응, 자동화 역량을 실습하기 위한 프로젝트입니다.

단순히 클라우드 서비스를 사용하는 것이 아니라, 실제 Private Cloud 운영 환경을 가정하여 OpenStack 리소스를 직접 구성하고, Prometheus/Grafana 기반 모니터링과 Python/Ansible 기반 장애 감지 및 자동 복구 기능을 구현하는 것을 목표로 합니다.

---

## 2. 프로젝트 핵심 목표

- OpenStack 기반 Private Cloud 구축
- VM, Network, Storage, User/Role 운영
- Prometheus/Grafana 기반 인프라 모니터링
- Python 기반 VM 상태 감지
- 장애 발생 시 자동 복구 스크립트 실행
- Ansible을 활용한 서버 초기 설정 자동화
- 장애 시나리오 및 트러블슈팅 문서화
- GitHub README 및 블로그 기반 포트폴리오 정리

---

## 3. 기술 스택

| 구분 | 기술 |
|---|---|
| OS | Ubuntu Server 24.04 LTS |
| Private Cloud | OpenStack / Canonical OpenStack Sunbeam |
| Compute | Nova |
| Network | Neutron |
| Storage | Glance, Cinder |
| Identity | Keystone |
| Dashboard | Horizon |
| Monitoring | Prometheus, Grafana, Node Exporter |
| Automation | Python, Shell Script, Ansible |
| Web Server | Nginx |
| Documentation | Markdown, GitHub README, Blog |
| Version Control | Git, GitHub |

---

## 4. 시스템 아키텍처

```text
[MacBook - 개발/관리 환경]
  |
  | SSH / Git / VS Code
  v
[amd64 Ubuntu Server - OpenStack Lab]
  |
  | OpenStack
  |
  ├── Keystone  : User / Project / Role 관리
  ├── Nova      : VM Instance 관리
  ├── Neutron   : Network / Router / Floating IP 관리
  ├── Glance    : Image 관리
  ├── Cinder    : Volume / Block Storage 관리
  └── Horizon   : Web Dashboard

[OpenStack VM]
  |
  ├── web-01      : Nginx + Node Exporter
  ├── db-01       : DB Test Server + Node Exporter
  ├── monitor-01  : Prometheus + Grafana + Node Exporter
  └── test-01     : 장애 테스트용 VM + Node Exporter

[Automation Layer]
  |
  ├── Python VM Health Checker
  ├── Auto Recovery Script
  ├── Incident Report Generator
  ├── Shell Script
  └── Ansible Playbook
```

상세 설계 문서: [`docs/architecture.md`](docs/architecture.md)

---

## 5. 주요 기능

## 5.1 OpenStack 구축

Ubuntu Server 환경에서 OpenStack 기반 Private Cloud를 구축합니다.

주요 작업:

- OpenStack 설치
- Horizon Dashboard 접속
- OpenStack CLI 설정
- 기본 네트워크 구성
- VM 생성 가능 상태 확인

문서: [`docs/openstack-install.md`](docs/openstack-install.md)

---

## 5.2 VM / Network / Storage / User 관리

OpenStack의 핵심 리소스를 직접 운영합니다.

관리 항목:

| 구분 | 내용 |
|---|---|
| VM | Instance 생성, 중지, 삭제, 상태 확인 |
| Network | Private Network, Subnet, Router, Floating IP |
| Security | Security Group, SSH/HTTP 포트 제어 |
| Storage | Image 등록, Volume 생성 및 연결 |
| User | Project, User, Role 생성 및 권한 관리 |

문서: [`docs/openstack-resource-management.md`](docs/openstack-resource-management.md)

---

## 5.3 Prometheus / Grafana 모니터링

OpenStack Host 및 VM의 자원 상태를 모니터링합니다.

수집 지표:

- CPU 사용률
- Memory 사용률
- Disk 사용률
- Network Traffic
- 서버 Up/Down 상태
- Nginx 상태

구성 요소:

```text
Node Exporter → Prometheus → Grafana Dashboard
```

문서: [`docs/monitoring-guide.md`](docs/monitoring-guide.md)

---

## 5.4 Python 기반 VM Health Checker

Python 스크립트를 통해 OpenStack VM 상태를 점검합니다.

감지 대상:

- VM 상태가 `ACTIVE`가 아닌 경우
- VM 상태가 `SHUTOFF`인 경우
- VM 상태가 `ERROR`인 경우
- 관리 대상 VM이 존재하지 않는 경우

실행 예시:

```bash
python automation/vm_health_checker.py
```

출력 예시:

```text
[OK] web-01 status: ACTIVE
[OK] db-01 status: ACTIVE
[WARN] test-01 status: SHUTOFF, expected: ACTIVE
[ACTION_REQUIRED] test-01 needs recovery
```

문서: [`docs/vm-health-checker.md`](docs/vm-health-checker.md)

---

## 5.5 자동 복구

Health Checker가 비정상 VM을 감지하면 자동 복구 스크립트를 실행합니다.

복구 대상:

| 장애 상태 | 처리 방식 |
|---|---|
| SHUTOFF | `openstack server start <VM_NAME>` 실행 |
| ERROR | 자동 복구 제외, Incident Report 생성 |
| UNKNOWN | 수동 점검 대상으로 분류 |

복구 흐름:

```text
VM 상태 감지
   ↓
장애 상태 분류
   ↓
복구 명령 실행
   ↓
상태 재확인
   ↓
로그 저장
   ↓
Incident Report 생성
```

문서: [`docs/auto-recovery.md`](docs/auto-recovery.md)

---

## 5.6 Ansible 서버 초기 설정 자동화

신규 VM 생성 후 반복되는 초기 설정 작업을 Ansible로 자동화합니다.

자동화 항목:

- 공통 패키지 설치
- 운영 계정 생성
- sudo 권한 설정
- 타임존 설정
- Nginx 설치
- Node Exporter 설치
- systemd 서비스 등록

문서: [`docs/ansible-guide.md`](docs/ansible-guide.md)

---

## 6. 장애 시나리오

본 프로젝트에서는 실제 운영 상황을 가정하여 4가지 핵심 장애 시나리오를 테스트합니다.

| 번호 | 장애 시나리오 | 감지 방식 | 대응 방식 |
|---|---|---|---|
| INCIDENT-001 | VM 비정상 종료 | OpenStack VM 상태 확인 | VM 자동 시작 |
| INCIDENT-002 | Nginx 서비스 중지 | systemctl / HTTP 확인 | Nginx 재시작 |
| INCIDENT-003 | 디스크 사용량 초과 | df 명령어 기반 확인 | 임시 파일/로그 정리 |
| INCIDENT-004 | CPU 과부하 | Grafana / top / ps 확인 | 원인 프로세스 확인 및 종료 |

장애 보고서:

- [`reports/incident-001-vm-shutoff.md`](reports/incident-001-vm-shutoff.md)
- [`reports/incident-002-nginx-down.md`](reports/incident-002-nginx-down.md)
- [`reports/incident-003-disk-full.md`](reports/incident-003-disk-full.md)
- [`reports/incident-004-cpu-high.md`](reports/incident-004-cpu-high.md)

---

## 7. 프로젝트 폴더 구조

```text
openstack-private-cloud-ops/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── openstack-install.md
│   ├── openstack-resource-management.md
│   ├── monitoring-guide.md
│   ├── vm-health-checker.md
│   ├── auto-recovery.md
│   ├── ansible-guide.md
│   └── troubleshooting/
│       ├── 01-openstack-install-error.md
│       ├── 02-vm-ssh-connection-failed.md
│       ├── 03-floating-ip-error.md
│       ├── 04-security-group-http-blocked.md
│       ├── 05-prometheus-target-down.md
│       └── 06-ansible-ssh-permission-error.md
│
├── automation/
│   ├── config.yaml
│   ├── openstack_client.py
│   ├── vm_health_checker.py
│   ├── service_health_checker.py
│   ├── auto_recovery.py
│   └── incident_report.py
│
├── scripts/
│   ├── check_disk_usage.sh
│   ├── check_service_status.sh
│   ├── restart_service.sh
│   └── generate_cpu_load.sh
│
├── ansible/
│   ├── inventory.ini
│   ├── site.yml
│   └── roles/
│       ├── common/
│       ├── nginx/
│       └── node_exporter/
│
├── monitoring/
│   ├── docker-compose.yml
│   └── prometheus.yml
│
├── reports/
│   ├── incident-001-vm-shutoff.md
│   ├── incident-002-nginx-down.md
│   ├── incident-003-disk-full.md
│   └── incident-004-cpu-high.md
│
├── screenshots/
└── blog/
```

---

## 8. 실행 순서

## 8.1 OpenStack 설치

```bash
sudo apt update
sudo apt upgrade -y
sudo snap install openstack
sunbeam prepare-node-script --bootstrap | bash -x
newgrp snap_daemon
sunbeam cluster bootstrap --accept-defaults --role control,compute,storage
sunbeam configure --accept-defaults --openrc demo-openrc
source demo-openrc
openstack service list
```

자세한 절차: [`docs/openstack-install.md`](docs/openstack-install.md)

---

## 8.2 VM 및 네트워크 구성

```bash
openstack network create private-network
openstack subnet create private-subnet \
  --network private-network \
  --subnet-range 10.0.0.0/24 \
  --gateway 10.0.0.1 \
  --dns-nameserver 8.8.8.8

openstack router create lab-router
openstack router add subnet lab-router private-subnet
```

자세한 절차: [`docs/openstack-resource-management.md`](docs/openstack-resource-management.md)

---

## 8.3 Ansible 초기 설정 실행

```bash
cd ansible
ansible all_servers -i inventory.ini -m ping
ansible-playbook -i inventory.ini site.yml
```

---

## 8.4 모니터링 실행

```bash
cd monitoring
docker compose up -d
```

접속:

```text
Prometheus: http://<MONITOR_FLOATING_IP>:9090
Grafana: http://<MONITOR_FLOATING_IP>:3000
```

---

## 8.5 VM Health Checker 실행

```bash
source .venv/bin/activate
python automation/vm_health_checker.py
```

---

## 9. 주요 코드 설명

## 9.1 OpenStack Client

파일:

```text
automation/openstack_client.py
```

역할:

- OpenStack CLI 명령어 실행
- VM 목록 조회
- VM 상세 조회
- VM 시작/중지 명령 실행

---

## 9.2 VM Health Checker

파일:

```text
automation/vm_health_checker.py
```

역할:

- 관리 대상 VM 상태 확인
- 정상/비정상 상태 판단
- 장애 로그 기록
- 자동 복구 스크립트 호출

---

## 9.3 Auto Recovery

파일:

```text
automation/auto_recovery.py
```

역할:

- 비정상 VM 상태별 복구 방식 분기
- SHUTOFF VM 자동 시작
- 복구 후 상태 재확인
- 복구 성공/실패 로그 기록

---

## 9.4 Incident Report Generator

파일:

```text
automation/incident_report.py
```

역할:

- 장애 대응 결과를 Markdown 보고서로 생성
- 장애 발생 시간, 대상, 상태, 복구 작업, 결과 기록

---

## 10. 트러블슈팅 문서

프로젝트 진행 중 발생 가능한 문제를 문서화합니다.

| 문서 | 내용 |
|---|---|
| [`02-vm-ssh-connection-failed.md`](docs/troubleshooting/02-vm-ssh-connection-failed.md) | VM SSH 접속 실패 |
| [`03-floating-ip-error.md`](docs/troubleshooting/03-floating-ip-error.md) | Floating IP 연결 오류 |
| [`04-security-group-http-blocked.md`](docs/troubleshooting/04-security-group-http-blocked.md) | Security Group HTTP 차단 |
| [`05-prometheus-target-down.md`](docs/troubleshooting/05-prometheus-target-down.md) | Prometheus Target DOWN |
| [`06-ansible-ssh-permission-error.md`](docs/troubleshooting/06-ansible-ssh-permission-error.md) | Ansible SSH 권한 오류 |

---

## 11. README에 추가할 스크린샷

실제 구축 후 아래 이미지를 `screenshots/`에 추가합니다.

| 파일명 | 내용 |
|---|---|
| `openstack-dashboard.png` | Horizon Dashboard |
| `vm-list.png` | OpenStack VM 목록 |
| `network-topology.png` | Network Topology |
| `volume-list.png` | Cinder Volume 목록 |
| `user-role-list.png` | User / Project / Role 목록 |
| `prometheus-targets.png` | Prometheus Targets UP 상태 |
| `grafana-dashboard.png` | Grafana Dashboard |
| `ansible-playbook-result.png` | Ansible 실행 결과 |
| `auto-recovery-log.png` | 자동 복구 로그 |
| `incident-report.png` | Incident Report 생성 결과 |

README에는 아래 형식으로 이미지를 추가합니다.

```md
![OpenStack Dashboard](screenshots/openstack-dashboard.png)
```

---

## 12. 프로젝트를 통해 증명할 수 있는 역량

이 프로젝트를 통해 다음 역량을 보여줄 수 있습니다.

- Linux 서버 운영 능력
- OpenStack 기반 Private Cloud 이해
- VM, Network, Storage, User 운영 경험
- Security Group 및 Floating IP 기반 네트워크 운영 경험
- Prometheus/Grafana 기반 모니터링 구성 능력
- 장애 감지 및 원인 분석 능력
- Python/Shell Script 기반 자동화 능력
- Ansible 기반 서버 초기 설정 자동화 능력
- 장애 대응 문서화 및 트러블슈팅 능력

---

## 13. 향후 개선 방향

- Slack 또는 Email 알림 연동
- Grafana Alerting 연동
- OpenStack API SDK 기반 자동화 고도화
- Terraform 기반 OpenStack 리소스 생성 자동화
- CI/CD 파이프라인 추가
- 장애 리포트 자동 요약 기능 추가
- LLM 기반 장애 원인 분석 기능 추가

---

## 14. 프로젝트 상태

| 단계 | 상태 |
|---|---|
| 프로젝트 구조 생성 | 완료 |
| 아키텍처 문서 작성 | 완료 |
| OpenStack 설치 문서 작성 | 완료 |
| 리소스 관리 문서 작성 | 완료 |
| 모니터링 문서 작성 | 완료 |
| Python VM Health Checker 구현 | 완료 |
| Auto Recovery 구현 | 완료 |
| Ansible 자동화 구성 | 완료 |
| 장애 시나리오 문서화 | 완료 |
| 트러블슈팅 문서화 | 진행 중 |
| 실제 OpenStack 구축 및 캡처 | 예정 |
| 블로그 작성 | 예정 |

---

## 15. 한 줄 요약

OpenStack 기반 Private Cloud 환경을 구축하고, VM/Network/Storage/User 운영부터 모니터링, 장애 감지, 자동 복구, Ansible 자동화까지 구현한 클라우드 운영 포트폴리오 프로젝트입니다.