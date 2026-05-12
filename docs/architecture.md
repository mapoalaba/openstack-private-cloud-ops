# 시스템 아키텍처 설계서

## 1. 문서 목적

본 문서는 `OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템`의 전체 구조를 설명하기 위한 아키텍처 문서이다.

이 프로젝트는 단순히 OpenStack을 설치하는 것이 아니라, 실제 클라우드 운영 환경을 가정하여 다음 요소를 통합적으로 구성하는 것을 목표로 한다.

- OpenStack 기반 Private Cloud 구축
- VM / Network / Storage / User 운영
- Prometheus / Grafana 기반 모니터링
- Python 기반 장애 감지
- 자동 복구 스크립트
- Ansible 기반 서버 초기 설정 자동화
- 장애 시나리오 및 트러블슈팅 문서화

---

## 2. 전체 아키텍처 개요

```text
[MacBook - 개발/관리 환경]
  |
  | SSH / Git / VS Code
  v
[amd64 Ubuntu Server - OpenStack Lab]
  |
  | OpenStack
  |
  ├── Keystone
  │     └── User / Project / Role 관리
  |
  ├── Nova
  │     └── VM Instance 생성 및 상태 관리
  |
  ├── Neutron
  │     └── Network / Subnet / Router / Floating IP 관리
  |
  ├── Glance
  │     └── VM Image 관리
  |
  ├── Cinder
  │     └── Volume / Block Storage 관리
  |
  └── Horizon
        └── OpenStack Web Dashboard

[OpenStack VM]
  |
  ├── web-01
  │     ├── Nginx
  │     └── Node Exporter
  |
  ├── db-01
  │     ├── Database Test Server
  │     └── Node Exporter
  |
  ├── monitor-01
  │     ├── Prometheus
  │     └── Grafana
  |
  └── test-01
        ├── 장애 테스트용 VM
        └── Node Exporter

[Automation Layer]
  |
  ├── Python VM Health Checker
  ├── Service Health Checker
  ├── Auto Recovery Script
  ├── Shell Script
  └── Ansible Playbook
```

---

## 3. 환경 구성

### 3.1 개발 및 관리 환경

| 항목 | 내용 |
|---|---|
| 장비 | MacBook |
| CPU Architecture | arm64 |
| 역할 | 코드 작성, 문서화, GitHub 관리, SSH 접속 |
| 주요 도구 | VS Code, Git, SSH, Python, Ansible |

Apple Silicon Mac에서는 OpenStack 전체 구동 및 중첩 가상화 실습에 제약이 있을 수 있으므로, MacBook은 개발 및 관리 환경으로 사용한다.

---

### 3.2 OpenStack 실행 환경

| 항목 | 내용 |
|---|---|
| 장비 | 별도 amd64 Ubuntu Server |
| OS | Ubuntu Server 24.04 LTS |
| CPU | Intel 또는 AMD |
| Memory | 최소 16GB, 권장 32GB |
| Disk | 최소 100GB, 권장 256GB 이상 |
| 역할 | OpenStack 구축, VM 생성, 네트워크/스토리지 운영 |

OpenStack은 실제 VM 생성과 네트워크 구성을 수행해야 하므로 amd64 기반 Ubuntu 서버에서 구축한다.

---

## 4. OpenStack 구성 요소

### 4.1 Keystone

Keystone은 OpenStack의 인증 및 권한 관리 서비스이다.

본 프로젝트에서는 다음 항목을 관리한다.

- Project 생성
- User 생성
- Role 부여
- 운영자 계정과 일반 사용자 계정 분리
- 권한 차이에 따른 접근 테스트

예상 구성:

| Project | User | Role |
|---|---|---|
| ops-project | ops-admin | admin |
| dev-project | dev-user | member |
| test-project | readonly-user | reader |

---

### 4.2 Nova

Nova는 OpenStack의 Compute 서비스이다.

본 프로젝트에서는 Nova를 통해 VM 인스턴스를 생성하고 상태를 관리한다.

운영 대상 VM:

| VM 이름 | 역할 |
|---|---|
| web-01 | Nginx 웹 서버 |
| db-01 | 데이터베이스 테스트 서버 |
| monitor-01 | Prometheus / Grafana 모니터링 서버 |
| test-01 | 장애 시나리오 테스트 서버 |

관리 항목:

- VM 생성
- VM 시작 / 중지
- VM 상태 확인
- VM 장애 감지
- VM 자동 복구

---

### 4.3 Neutron

Neutron은 OpenStack의 네트워크 서비스이다.

본 프로젝트에서는 Private Cloud 내부 네트워크와 외부 접속 구성을 실습한다.

네트워크 구성:

```text
[External Network]
        |
     Router
        |
[Private Network: 10.0.0.0/24]
        |
 ├── web-01
 ├── db-01
 ├── monitor-01
 └── test-01
```

관리 항목:

- Private Network 생성
- Subnet 생성
- Router 생성
- Floating IP 연결
- Security Group 설정
- SSH / HTTP 접근 제어

---

### 4.4 Glance

Glance는 OpenStack의 이미지 관리 서비스이다.

본 프로젝트에서는 VM 생성을 위한 Ubuntu Cloud Image를 관리한다.

관리 항목:

- Ubuntu Cloud Image 등록
- 이미지 목록 확인
- 이미지 기반 VM 생성

---

### 4.5 Cinder

Cinder는 OpenStack의 Block Storage 서비스이다.

본 프로젝트에서는 VM에 추가 볼륨을 연결하고, 데이터 보존 여부를 확인한다.

관리 항목:

- Volume 생성
- VM에 Volume Attach
- 파일 시스템 생성
- Mount 설정
- Volume Detach / Reattach 테스트

---

### 4.6 Horizon

Horizon은 OpenStack의 Web Dashboard이다.

본 프로젝트에서는 Horizon을 통해 다음 항목을 시각적으로 확인한다.

- VM 목록
- Network Topology
- Volume 목록
- User / Project / Role
- Floating IP
- Security Group

README와 블로그에는 Horizon 화면 캡처를 포함하여 구축 결과를 시각적으로 보여준다.

---

## 5. 모니터링 아키텍처

본 프로젝트에서는 Prometheus, Node Exporter, Grafana를 사용하여 서버 상태를 모니터링한다.

```text
[web-01]          Node Exporter
[db-01]           Node Exporter
[test-01]         Node Exporter
[OpenStack Host]  Node Exporter
        |
        v
[monitor-01] Prometheus
        |
        v
[monitor-01] Grafana Dashboard
```

수집 지표:

| 지표 | 설명 |
|---|---|
| CPU Usage | 서버 CPU 사용률 |
| Memory Usage | 메모리 사용률 |
| Disk Usage | 디스크 사용률 |
| Network Traffic | 네트워크 송수신량 |
| Instance Up/Down | 서버 응답 상태 |
| Nginx Status | 웹 서비스 응답 상태 |

Grafana 대시보드에는 다음 패널을 구성한다.

- 전체 서버 상태
- VM별 CPU 사용률
- VM별 Memory 사용률
- VM별 Disk 사용률
- 네트워크 트래픽
- 장애 발생 현황

---

## 6. 자동화 아키텍처

자동화 계층은 Python, Shell Script, Ansible로 구성한다.

```text
[Python Health Checker]
        |
        | 장애 감지
        v
[Auto Recovery Script]
        |
        | 복구 명령 실행
        v
[OpenStack CLI / SSH / Shell Script]
        |
        | 복구 후 확인
        v
[Incident Report]
```

---

### 6.1 Python Health Checker

Python 스크립트는 VM 및 서비스 상태를 주기적으로 점검한다.

감지 항목:

- VM 상태가 `ACTIVE`가 아닌 경우
- VM 상태가 `SHUTOFF`인 경우
- VM 상태가 `ERROR`인 경우
- HTTP 응답 실패
- Floating IP 미할당
- 디스크 사용량 초과
- CPU 사용률 초과

주요 파일:

```text
automation/
├── openstack_client.py
├── vm_health_checker.py
├── service_health_checker.py
└── config.yaml
```

---

### 6.2 Auto Recovery

장애가 감지되면 장애 유형에 따라 복구 작업을 실행한다.

| 장애 유형 | 복구 방식 |
|---|---|
| VM 종료 | OpenStack CLI/API로 VM 재시작 |
| Nginx 중지 | SSH 접속 후 `systemctl restart nginx` |
| 디스크 사용량 초과 | 임시 파일 및 로그 정리 |
| CPU 과부하 | 상위 프로세스 기록 및 필요 시 종료 |
| HTTP 응답 실패 | Nginx 재시작 또는 VM 재부팅 |

주요 파일:

```text
automation/
├── auto_recovery.py
├── incident_report.py
```

---

### 6.3 Shell Script

Shell Script는 단일 서버 내부 상태 점검과 복구 작업에 사용한다.

주요 파일:

```text
scripts/
├── check_disk_usage.sh
├── check_service_status.sh
├── restart_service.sh
└── generate_cpu_load.sh
```

용도:

- 디스크 사용량 확인
- 서비스 상태 확인
- 서비스 재시작
- CPU 부하 테스트 생성

---

### 6.4 Ansible

Ansible은 신규 VM 생성 후 반복되는 초기 설정을 자동화한다.

자동화 항목:

- 패키지 업데이트
- 필수 패키지 설치
- Nginx 설치
- Node Exporter 설치
- 운영 계정 생성
- SSH 설정
- 기본 보안 설정

구조:

```text
ansible/
├── inventory.ini
├── site.yml
└── roles/
    ├── common/
    ├── nginx/
    └── node_exporter/
```

---

## 7. 장애 대응 흐름

장애 대응은 다음 흐름으로 진행된다.

```text
1. 장애 발생
   ↓
2. Python Health Checker가 상태 점검
   ↓
3. 장애 유형 분류
   ↓
4. Auto Recovery Script 실행
   ↓
5. 복구 후 상태 재확인
   ↓
6. 성공/실패 로그 저장
   ↓
7. Incident Report 생성
```

---

## 8. 장애 시나리오 설계

본 프로젝트에서는 최소 4개 이상의 장애 시나리오를 테스트한다.

| 번호 | 장애 시나리오 | 발생 방법 | 감지 방식 | 복구 방식 |
|---|---|---|---|---|
| 1 | VM 비정상 종료 | `openstack server stop test-01` | VM 상태 SHUTOFF 확인 | VM 자동 시작 |
| 2 | Nginx 서비스 중지 | `systemctl stop nginx` | HTTP 응답 실패 | Nginx 재시작 |
| 3 | 디스크 사용량 초과 | dummy file 생성 | Disk usage 임계치 초과 | 임시 파일 정리 |
| 4 | CPU 과부하 | `stress` 실행 | CPU usage 임계치 초과 | 프로세스 기록 및 조치 |
| 5 | Floating IP 미할당 | Floating IP 제거 | 외부 접속 실패 | 원인 보고 |
| 6 | Security Group 포트 차단 | 80/22 포트 차단 | 서비스 정상이나 접속 실패 | 규칙 수정 |

---

## 9. 로그 및 보고서 구조

장애 감지와 복구 결과는 로그와 보고서로 남긴다.

예상 로그 구조:

```text
logs/
├── vm-health-check.log
├── service-health-check.log
└── recovery.log
```

장애 보고서 구조:

```text
reports/
├── incident-001-vm-shutoff.md
├── incident-002-nginx-down.md
├── incident-003-disk-full.md
└── incident-004-cpu-high.md
```

보고서에는 다음 항목을 포함한다.

- 장애 발생 시간
- 장애 대상
- 장애 유형
- 감지 방법
- 원인 분석
- 복구 절차
- 복구 결과
- 재발 방지 방안

---

## 10. 보안 고려사항

본 프로젝트는 학습용 Private Cloud 환경이지만, 기본적인 보안 설정을 적용한다.

보안 적용 항목:

- SSH 접근 제한
- Security Group 최소 허용
- 운영자 계정과 일반 사용자 계정 분리
- OpenStack 인증 정보 GitHub 업로드 제외
- `.gitignore`를 통한 openrc, clouds.yaml 제외
- 관리자 권한 최소화 원칙 적용

---

## 11. 산출물

최종 산출물은 다음과 같다.

| 구분 | 산출물 |
|---|---|
| 구축 문서 | OpenStack 설치 문서 |
| 운영 문서 | VM / Network / Storage / User 관리 문서 |
| 모니터링 문서 | Prometheus / Grafana 설정 문서 |
| 자동화 코드 | Python Health Checker, Auto Recovery |
| Ansible | 서버 초기 설정 Playbook |
| 장애 보고서 | 장애 시나리오별 Incident Report |
| 트러블슈팅 | 오류 및 해결 과정 문서 |
| 포트폴리오 | GitHub README, Blog 게시글 |

---

## 12. 기대 효과

이 아키텍처를 통해 다음 역량을 보여줄 수 있다.

- Linux 서버 운영 능력
- OpenStack 기반 Private Cloud 이해
- VM, Network, Storage, User 운영 경험
- 모니터링 시스템 구성 능력
- 장애 감지 및 자동 복구 구현 능력
- Ansible 기반 서버 초기 설정 자동화 능력
- 트러블슈팅 및 문서화 능력
