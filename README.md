# OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템

## 1. 프로젝트 개요

본 프로젝트는 신입 Cloud Engineer 직무에서 요구되는 Linux 서버 운영, OpenStack 기반 Private Cloud 구축, VM/Network/Storage/User 관리, 모니터링, 장애 대응, 자동화 역량을 실습하기 위한 프로젝트입니다.

Ubuntu Server 환경에서 OpenStack 기반 Private Cloud를 구축하고, Prometheus/Grafana를 활용한 모니터링 대시보드와 Python/Ansible 기반 장애 감지 및 자동 복구 기능을 구현하는 것을 목표로 합니다.

---

## 2. 프로젝트 목적

이 프로젝트의 핵심 목적은 단순히 클라우드 서비스를 사용하는 것이 아니라, 클라우드 운영자가 실제로 수행하는 인프라 운영 업무를 직접 구현해보는 것입니다.

주요 목표는 다음과 같습니다.

- OpenStack 기반 Private Cloud 구축
- VM, Network, Storage, User/Role 운영
- Prometheus/Grafana 기반 인프라 모니터링
- Python 기반 VM 및 서비스 상태 감지
- 장애 발생 시 자동 복구 스크립트 실행
- Ansible을 활용한 서버 초기 설정 자동화
- 장애 시나리오 및 트러블슈팅 문서화

---

## 3. 기술 스택

| 구분 | 기술 |
|---|---|
| OS | Ubuntu Server 24.04 LTS |
| Private Cloud | OpenStack / Canonical OpenStack Sunbeam |
| Monitoring | Prometheus, Grafana, Node Exporter |
| Automation | Python, Shell Script, Ansible |
| Web Server | Nginx |
| Documentation | Markdown, GitHub README, Blog |
| Version Control | Git, GitHub |

---

## 4. 시스템 아키텍처

```text
[MacBook]
  |
  | SSH / Git / Documentation
  v
[amd64 Ubuntu Server]
  |
  | OpenStack
  |
  ├── Keystone  : User / Project / Role 관리
  ├── Nova      : VM Instance 관리
  ├── Neutron   : Network / Router / Floating IP 관리
  ├── Glance    : Image 관리
  ├── Cinder    : Volume / Storage 관리
  └── Horizon   : Web Dashboard

[Monitoring]
  ├── Prometheus
  ├── Node Exporter
  └── Grafana

[Automation]
  ├── Python VM Health Checker
  ├── Auto Recovery Script
  ├── Shell Script
  └── Ansible Playbook