# Ansible Guide

## 1. 문서 목적

본 문서는 `OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템` 프로젝트에서 Ansible을 활용하여 OpenStack VM의 초기 설정을 자동화하는 방법을 정리한 문서이다.

Ansible을 사용하면 VM 생성 후 반복적으로 수행되는 패키지 설치, 서비스 구성, 모니터링 에이전트 설치 작업을 자동화할 수 있다.

---

## 2. 자동화 목표

본 프로젝트에서 Ansible로 자동화할 작업은 다음과 같다.

- 공통 패키지 설치
- 운영 계정 생성
- sudo 권한 설정
- 타임존 설정
- Nginx 설치
- Node Exporter 설치
- systemd 서비스 등록

---

## 3. Ansible 구조

```text
ansible/
├── inventory.ini
├── site.yml
└── roles/
    ├── common/
    │   └── tasks/main.yml
    ├── nginx/
    │   └── tasks/main.yml
    └── node_exporter/
        └── tasks/main.yml
```

---

## 4. Inventory 구성

`ansible/inventory.ini`

```ini
[web]
web-01 ansible_host=<WEB_01_FLOATING_IP> ansible_user=ubuntu ansible_ssh_private_key_file=../lab-key.pem

[db]
db-01 ansible_host=<DB_01_FLOATING_IP> ansible_user=ubuntu ansible_ssh_private_key_file=../lab-key.pem

[monitor]
monitor-01 ansible_host=<MONITOR_01_FLOATING_IP> ansible_user=ubuntu ansible_ssh_private_key_file=../lab-key.pem

[test]
test-01 ansible_host=<TEST_01_FLOATING_IP> ansible_user=ubuntu ansible_ssh_private_key_file=../lab-key.pem

[all_servers:children]
web
db
monitor
test
```

각 VM에 Floating IP를 연결한 뒤 `<...>` 값을 실제 IP로 변경한다.

---

## 5. Playbook 구성

`ansible/site.yml`

```yaml
- name: Configure all OpenStack lab servers
  hosts: all_servers
  become: true
  roles:
    - common
    - node_exporter

- name: Configure web servers
  hosts: web
  become: true
  roles:
    - nginx
```

구성 의미:

| 대상 | 적용 Role |
|---|---|
| all_servers | common, node_exporter |
| web | nginx |

---

## 6. Role 설명

## 6.1 common Role

`common` Role은 모든 서버에 적용되는 기본 설정이다.

작업 내용:

- apt cache 업데이트
- 패키지 업그레이드
- 공통 패키지 설치
- ops 운영 계정 생성
- sudo 권한 설정
- Asia/Seoul 타임존 설정

---

## 6.2 nginx Role

`nginx` Role은 web 서버에만 적용된다.

작업 내용:

- Nginx 설치
- Nginx 서비스 시작
- 부팅 시 자동 실행 설정
- 테스트용 index.html 생성

---

## 6.3 node_exporter Role

`node_exporter` Role은 모든 서버에 적용된다.

작업 내용:

- node_exporter 시스템 사용자 생성
- Node Exporter 다운로드
- 바이너리 복사
- systemd 서비스 생성
- 서비스 시작 및 자동 실행 설정

---

## 7. 실행 전 사전 조건

Ansible 실행 전 다음 항목이 완료되어야 한다.

- OpenStack VM 생성 완료
- 각 VM에 Floating IP 연결 완료
- Security Group에서 SSH 22번 포트 허용
- SSH Key Pair 준비 완료
- `inventory.ini`에 실제 IP 입력 완료
- 관리 PC에서 각 VM으로 SSH 접속 가능

SSH 테스트:

```bash
ssh -i lab-key.pem ubuntu@<VM_FLOATING_IP>
```

---

## 8. Ansible 설치

Mac:

```bash
brew install ansible
```

Ubuntu:

```bash
sudo apt update
sudo apt install -y ansible
```

설치 확인:

```bash
ansible --version
```

---

## 9. 연결 테스트

`ansible/` 디렉터리에서 실행한다.

```bash
cd ansible
ansible all_servers -i inventory.ini -m ping
```

정상 결과:

```text
web-01 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

---

## 10. Playbook 실행

전체 서버 초기 설정:

```bash
ansible-playbook -i inventory.ini site.yml
```

특정 서버만 실행:

```bash
ansible-playbook -i inventory.ini site.yml --limit web-01
```

문법 검사:

```bash
ansible-playbook -i inventory.ini site.yml --syntax-check
```

실제 변경 없이 미리 확인:

```bash
ansible-playbook -i inventory.ini site.yml --check
```

---

## 11. 실행 후 확인

## 11.1 Node Exporter 확인

각 서버에서:

```bash
systemctl status node_exporter
```

또는 관리 PC에서:

```bash
curl http://<VM_FLOATING_IP>:9100/metrics
```

---

## 11.2 Nginx 확인

web-01에서:

```bash
systemctl status nginx
```

관리 PC에서:

```bash
curl http://<WEB_01_FLOATING_IP>
```

예상 결과:

```html
<h1>OpenStack Private Cloud Lab - web-01</h1>
<p>This server is managed by Ansible.</p>
```

---

## 12. 장애 시나리오와 연계

Ansible로 설치한 Nginx와 Node Exporter는 이후 장애 시나리오에 사용된다.

| 시나리오 | 대상 | 설명 |
|---|---|---|
| Nginx 서비스 중지 | web-01 | `systemctl stop nginx` 후 복구 테스트 |
| CPU 과부하 | test-01 | `stress`로 부하 발생 |
| Disk 사용량 초과 | test-01 | dummy file 생성 |
| 모니터링 장애 | 전체 VM | Node Exporter 중지 후 Prometheus Target DOWN 확인 |

---

## 13. 예상 오류 및 해결

## 13.1 SSH 연결 실패

증상:

```text
UNREACHABLE! => Failed to connect to the host via ssh
```

확인 항목:

- Floating IP가 연결되어 있는지
- Security Group에서 22번 포트가 열려 있는지
- Key Pair 경로가 맞는지
- VM의 기본 사용자가 `ubuntu`인지

확인 명령어:

```bash
ssh -i lab-key.pem ubuntu@<VM_FLOATING_IP>
```

---

## 13.2 Permission denied

증상:

```text
Permission denied (publickey)
```

해결:

```bash
chmod 600 lab-key.pem
```

Inventory의 키 경로 확인:

```ini
ansible_ssh_private_key_file=../lab-key.pem
```

---

## 13.3 sudo 권한 오류

증상:

```text
Missing sudo password
```

해결:

Ubuntu Cloud Image 기본 사용자인 `ubuntu`는 일반적으로 sudo 권한을 가진다.

필요 시 inventory에 다음 옵션을 추가한다.

```ini
ansible_become=true
```

또는 Playbook에서 `become: true`가 설정되어 있는지 확인한다.

---

## 13.4 Node Exporter 다운로드 실패

증상:

```text
Failed to connect to github.com
```

확인 항목:

- VM의 외부 인터넷 연결 가능 여부
- DNS 설정
- Router 및 External Network 설정
- Security Group outbound 규칙

확인 명령어:

```bash
ping 8.8.8.8
curl https://github.com
```

---

## 14. README에 사용할 캡처 목록

| 파일명 | 내용 |
|---|---|
| `screenshots/ansible-ping-success.png` | Ansible ping 성공 |
| `screenshots/ansible-playbook-result.png` | Playbook 실행 성공 |
| `screenshots/nginx-result.png` | Nginx 접속 결과 |
| `screenshots/node-exporter-metrics.png` | Node Exporter metrics 출력 |

---

## 15. 완료 기준

다음 항목이 완료되면 Ansible 자동화 단계가 완료된 것으로 판단한다.

- `inventory.ini` 작성 완료
- `site.yml` 작성 완료
- `common` Role 작성 완료
- `nginx` Role 작성 완료
- `node_exporter` Role 작성 완료
- Ansible ping 성공
- Playbook 실행 성공
- web-01에서 Nginx 접속 성공
- 모든 VM에서 Node Exporter metrics 확인