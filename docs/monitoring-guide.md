# Monitoring Guide

## 1. 문서 목적

본 문서는 `OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템` 프로젝트에서 Prometheus, Grafana, Node Exporter를 활용하여 OpenStack VM 및 Ubuntu 서버 상태를 모니터링하는 방법을 정리한 문서이다.

모니터링 시스템은 클라우드 운영자가 장애를 빠르게 인지하고 원인을 분석하기 위한 핵심 구성 요소이다.

---

## 2. 모니터링 구성 목표

본 프로젝트의 모니터링 목표는 다음과 같다.

- OpenStack Host 서버 상태 모니터링
- OpenStack VM 상태 모니터링
- CPU, Memory, Disk, Network 지표 수집
- Grafana Dashboard를 통한 시각화
- 장애 시나리오 발생 시 자원 변화 확인
- Python 기반 장애 감지 자동화와 연계

---

## 3. 모니터링 아키텍처

```text
[OpenStack Host]
  └── Node Exporter : 9100

[web-01]
  └── Node Exporter : 9100

[db-01]
  └── Node Exporter : 9100

[test-01]
  └── Node Exporter : 9100

[monitor-01]
  ├── Prometheus : 9090
  ├── Grafana    : 3000
  └── Node Exporter : 9100
```

데이터 흐름:

```text
Node Exporter
    ↓
Prometheus가 주기적으로 scrape
    ↓
Prometheus TSDB에 저장
    ↓
Grafana에서 Prometheus 데이터 조회
    ↓
Dashboard 시각화
```

---

## 4. 모니터링 대상

| 대상 | 역할 | 수집 방식 |
|---|---|---|
| OpenStack Host | OpenStack 실행 서버 | Node Exporter |
| web-01 | Nginx 웹 서버 | Node Exporter |
| db-01 | DB 테스트 서버 | Node Exporter |
| monitor-01 | 모니터링 서버 | Node Exporter |
| test-01 | 장애 테스트 서버 | Node Exporter |

---

## 5. 수집 지표

| 지표 | 설명 | 활용 목적 |
|---|---|---|
| CPU Usage | CPU 사용률 | CPU 과부하 감지 |
| Memory Usage | 메모리 사용률 | 메모리 부족 감지 |
| Disk Usage | 디스크 사용률 | 디스크 부족 감지 |
| Network Traffic | 네트워크 송수신량 | 트래픽 이상 감지 |
| Node Up | 서버 응답 상태 | 서버 Down 감지 |
| Load Average | 시스템 부하 | 부하 추세 분석 |

---

## 6. Security Group 포트 허용

Prometheus와 Grafana, Node Exporter 접근을 위해 다음 포트를 허용한다.

| 서비스 | 포트 | 설명 |
|---|---:|---|
| Prometheus | 9090 | Prometheus Web UI |
| Grafana | 3000 | Grafana Web UI |
| Node Exporter | 9100 | Linux 메트릭 수집 |

OpenStack Security Group 설정:

```bash
openstack security group rule create \
  --proto tcp \
  --dst-port 9090 \
  default

openstack security group rule create \
  --proto tcp \
  --dst-port 3000 \
  default

openstack security group rule create \
  --proto tcp \
  --dst-port 9100 \
  default
```

---

## 7. monitor-01에 Docker 설치

monitor-01 VM에 SSH 접속한다.

```bash
ssh -i lab-key.pem ubuntu@<MONITOR_FLOATING_IP>
```

패키지 업데이트:

```bash
sudo apt update
sudo apt upgrade -y
```

Docker 설치:

```bash
sudo apt install -y docker.io docker-compose-plugin
```

Docker 서비스 활성화:

```bash
sudo systemctl enable --now docker
```

현재 사용자를 docker 그룹에 추가:

```bash
sudo usermod -aG docker $USER
```

그룹 적용을 위해 로그아웃 후 다시 접속하거나 다음 명령어를 실행한다.

```bash
newgrp docker
```

Docker 동작 확인:

```bash
docker version
docker compose version
```

---

## 8. monitoring 디렉터리 구성

프로젝트의 `monitoring/` 디렉터리를 사용한다.

```text
monitoring/
├── docker-compose.yml
└── prometheus.yml
```

---

## 9. docker-compose.yml 작성

`monitoring/docker-compose.yml` 파일에 다음 내용을 작성한다.

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: private-cloud-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: private-cloud-grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:
```

---

## 10. prometheus.yml 작성

`monitoring/prometheus.yml` 파일에 다음 내용을 작성한다.

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "openstack-host"
    static_configs:
      - targets:
          - "<OPENSTACK_HOST_IP>:9100"

  - job_name: "openstack-vms"
    static_configs:
      - targets:
          - "<WEB_01_PRIVATE_IP>:9100"
          - "<DB_01_PRIVATE_IP>:9100"
          - "<MONITOR_01_PRIVATE_IP>:9100"
          - "<TEST_01_PRIVATE_IP>:9100"
```

실제 환경에 맞게 `<IP>` 값을 수정한다.

예시:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "openstack-host"
    static_configs:
      - targets:
          - "192.168.0.10:9100"

  - job_name: "openstack-vms"
    static_configs:
      - targets:
          - "10.0.0.11:9100"
          - "10.0.0.12:9100"
          - "10.0.0.13:9100"
          - "10.0.0.14:9100"
```

---

## 11. Node Exporter 설치

모니터링 대상 서버마다 Node Exporter를 설치한다.

대상:

```text
OpenStack Host
web-01
db-01
monitor-01
test-01
```

설치 명령어:

```bash
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz
tar xvf node_exporter-1.8.2.linux-amd64.tar.gz
sudo cp node_exporter-1.8.2.linux-amd64/node_exporter /usr/local/bin/
```

Node Exporter 사용자 생성:

```bash
sudo useradd --no-create-home --shell /bin/false node_exporter
```

권한 설정:

```bash
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

systemd 서비스 파일 생성:

```bash
sudo vim /etc/systemd/system/node_exporter.service
```

아래 내용 입력:

```ini
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

서비스 등록 및 실행:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
```

상태 확인:

```bash
sudo systemctl status node_exporter
```

포트 확인:

```bash
ss -tulnp | grep 9100
```

---

## 12. Prometheus / Grafana 실행

monitor-01의 `monitoring/` 디렉터리에서 실행한다.

```bash
cd monitoring
docker compose up -d
```

컨테이너 확인:

```bash
docker ps
```

로그 확인:

```bash
docker compose logs -f
```

---

## 13. Prometheus 접속 확인

브라우저에서 접속:

```text
http://<MONITOR_FLOATING_IP>:9090
```

Targets 확인:

```text
Status → Targets
```

모든 대상이 `UP` 상태인지 확인한다.

Prometheus에서 테스트할 쿼리:

```promql
up
```

CPU 관련 쿼리:

```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

Memory 사용률 쿼리:

```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

Disk 사용률 쿼리:

```promql
100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})
```

---

## 14. Grafana 접속 확인

브라우저에서 접속:

```text
http://<MONITOR_FLOATING_IP>:3000
```

기본 로그인 정보:

```text
ID: admin
Password: admin
```

최초 로그인 후 비밀번호를 변경한다.

---

## 15. Grafana Data Source 추가

Grafana에서 다음 순서로 Prometheus를 연결한다.

```text
Connections
→ Data sources
→ Add data source
→ Prometheus 선택
```

URL 입력:

```text
http://prometheus:9090
```

Docker Compose 내부 네트워크 기준으로 Grafana 컨테이너에서 Prometheus 컨테이너에 접근할 때는 서비스 이름인 `prometheus`를 사용한다.

저장 후 테스트:

```text
Save & test
```

---

## 16. Grafana Dashboard 구성

Dashboard에서 다음 패널을 만든다.

| 패널 | PromQL |
|---|---|
| Server UP | `up` |
| CPU Usage | `100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` |
| Memory Usage | `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100` |
| Disk Usage | `100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})` |
| Network Receive | `rate(node_network_receive_bytes_total[5m])` |
| Network Transmit | `rate(node_network_transmit_bytes_total[5m])` |

추천 패널 구성:

```text
1. 전체 서버 UP/DOWN 상태
2. VM별 CPU 사용률
3. VM별 Memory 사용률
4. VM별 Disk 사용률
5. VM별 Network Receive
6. VM별 Network Transmit
```

---

## 17. 장애 시나리오와 모니터링 연계

## 17.1 CPU 과부하 테스트

test-01에서 실행:

```bash
sudo apt install -y stress
stress --cpu 2 --timeout 120
```

Grafana에서 확인:

- CPU Usage 증가
- Load Average 증가

---

## 17.2 디스크 사용량 초과 테스트

test-01에서 실행:

```bash
fallocate -l 2G /tmp/dummy-file
```

Grafana에서 확인:

- Disk Usage 증가

테스트 후 제거:

```bash
rm /tmp/dummy-file
```

---

## 17.3 서버 Down 테스트

test-01 VM 중지:

```bash
openstack server stop test-01
```

Prometheus에서 확인:

```promql
up
```

해당 서버가 `0`으로 표시되는지 확인한다.

---

## 18. README에 사용할 캡처 목록

| 파일명 | 캡처 내용 |
|---|---|
| `screenshots/prometheus-main.png` | Prometheus 메인 화면 |
| `screenshots/prometheus-targets.png` | Prometheus Targets UP 상태 |
| `screenshots/grafana-dashboard.png` | Grafana 전체 대시보드 |
| `screenshots/grafana-cpu-high.png` | CPU 과부하 테스트 화면 |
| `screenshots/grafana-disk-usage.png` | Disk 사용률 증가 화면 |

---

## 19. 예상 오류 및 해결 방향

## 19.1 Prometheus Target DOWN

증상:

```text
Target 상태가 DOWN으로 표시됨
```

확인 항목:

```bash
curl http://<TARGET_IP>:9100/metrics
```

확인할 것:

- Node Exporter 서비스 실행 여부
- Security Group 9100 포트 허용 여부
- Prometheus 설정의 IP 주소가 정확한지
- VM 간 네트워크 통신 가능 여부

Node Exporter 상태 확인:

```bash
sudo systemctl status node_exporter
```

---

## 19.2 Grafana에서 Prometheus 연결 실패

증상:

```text
Data source connection failed
```

확인 항목:

- Grafana Data Source URL이 `http://prometheus:9090`인지 확인
- Prometheus 컨테이너가 실행 중인지 확인
- Docker Compose 서비스 이름이 `prometheus`인지 확인

확인 명령어:

```bash
docker ps
docker compose logs prometheus
docker compose logs grafana
```

---

## 19.3 3000 또는 9090 포트 접속 실패

확인 항목:

- Docker 컨테이너 실행 여부
- OpenStack Security Group 포트 허용 여부
- Floating IP 연결 여부
- 서버 방화벽 상태

확인 명령어:

```bash
docker ps
openstack security group rule list default
sudo ufw status
```

---

## 20. 완료 기준

다음 항목이 모두 완료되면 모니터링 단계가 완료된 것으로 판단한다.

- monitor-01에 Docker 설치 완료
- Prometheus 컨테이너 실행 완료
- Grafana 컨테이너 실행 완료
- OpenStack Host 및 VM에 Node Exporter 설치 완료
- Prometheus Targets가 UP 상태로 표시됨
- Grafana에서 Prometheus Data Source 연결 완료
- CPU / Memory / Disk / Network Dashboard 구성 완료
- 장애 시나리오 발생 시 Grafana에서 변화 확인 완료
- 주요 화면 캡처 완료

---

## 21. 다음 단계

다음 단계에서는 Python 기반으로 VM 및 서비스 상태를 감지하는 Health Checker를 구현한다.

다음 문서:

```text
docs/vm-health-checker.md
```