# Incident 002 - Nginx 서비스 중지 복구

## 1. 시나리오 개요

web-01 VM에서 Nginx 서비스가 중지된 상황을 가정하고, 서비스 상태 점검 스크립트를 통해 장애를 감지한 뒤 서비스를 재시작하는 시나리오이다.

---

## 2. 장애 정보

| 항목 | 내용 |
|---|---|
| 장애 번호 | INCIDENT-002 |
| 장애 유형 | Web Service Down |
| 대상 VM | web-01 |
| 대상 서비스 | nginx |
| 감지 방식 | systemctl 상태 확인 / HTTP 응답 확인 |
| 복구 방식 | `systemctl restart nginx` |

---

## 3. 장애 발생 명령어

web-01에서 실행:

```bash
sudo systemctl stop nginx
```

상태 확인:

```bash
systemctl status nginx
```

또는 외부에서 HTTP 확인:

```bash
curl http://<WEB_01_FLOATING_IP>
```

---

## 4. 감지 명령어

web-01에서 실행:

```bash
./scripts/check_service_status.sh nginx
```

예상 출력:

```text
[WARN] nginx is not running.
[ACTION_REQUIRED] Restart service.
```

---

## 5. 복구 명령어

```bash
./scripts/restart_service.sh nginx
```

또는 직접 실행:

```bash
sudo systemctl restart nginx
```

---

## 6. 복구 후 확인

```bash
systemctl status nginx
curl http://<WEB_01_FLOATING_IP>
```

예상 결과:

```text
[SUCCESS] nginx restarted successfully.
```

HTTP 응답:

```html
<h1>OpenStack Private Cloud Lab - web-01</h1>
<p>This server is managed by Ansible.</p>
```

---

## 7. 원인 분석

Nginx 서비스 중지는 다음 원인으로 발생할 수 있다.

- 운영자의 수동 중지
- 설정 파일 오류
- 포트 충돌
- 패키지 업데이트 후 서비스 실패
- 서버 리소스 부족

---

## 8. 재발 방지

- Nginx 서비스 상태 주기 점검
- systemd restart policy 적용
- Prometheus Blackbox Exporter를 통한 HTTP 상태 감시
- Nginx 설정 변경 전 문법 검사 수행

Nginx 설정 검사:

```bash
sudo nginx -t
```
