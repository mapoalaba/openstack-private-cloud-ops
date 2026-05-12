# Incident 004 - CPU 과부하 감지

## 1. 시나리오 개요

test-01 VM에서 stress 도구를 사용하여 CPU 과부하를 발생시키고, Prometheus/Grafana와 프로세스 확인 명령어를 통해 부하 상태를 분석하는 시나리오이다.

---

## 2. 장애 정보

| 항목 | 내용 |
|---|---|
| 장애 번호 | INCIDENT-004 |
| 장애 유형 | CPU Usage High |
| 대상 VM | test-01 |
| 감지 기준 | CPU usage 90% 이상 |
| 감지 방식 | Grafana Dashboard / top / ps |
| 복구 방식 | 원인 프로세스 확인 및 종료 |

---

## 3. 장애 발생 명령어

test-01에서 실행:

```bash
./scripts/generate_cpu_load.sh 2 120
```

또는 직접 실행:

```bash
sudo apt install -y stress
stress --cpu 2 --timeout 120
```

---

## 4. 감지 방법

Grafana Dashboard에서 확인:

- CPU Usage 증가
- Load Average 증가

서버 내부에서 확인:

```bash
top
```

또는:

```bash
ps aux --sort=-%cpu | head
```

---

## 5. 복구 방법

stress는 timeout이 지나면 자동 종료된다.

강제 종료가 필요한 경우:

```bash
pkill stress
```

복구 후 확인:

```bash
top
ps aux --sort=-%cpu | head
```

---

## 6. 원인 분석

CPU 과부하는 다음 원인으로 발생할 수 있다.

- 비정상 프로세스
- 무한 루프
- 트래픽 급증
- 배치 작업 집중
- 악성 스크립트 실행

---

## 7. 재발 방지

- CPU 사용률 임계치 알림 설정
- 비정상 프로세스 탐지
- 서비스별 리소스 제한 적용
- 중요 서버에 대한 Auto Scaling 또는 Scale-up 검토
- 장애 발생 시 프로세스 정보 자동 기록
