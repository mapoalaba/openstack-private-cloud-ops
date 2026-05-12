# OpenStack 설치 문서

## 1. 문서 목적

본 문서는 `OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템` 프로젝트에서 OpenStack 기반 Private Cloud 환경을 구축하기 위한 설치 절차를 정리한 문서이다.

이 프로젝트는 Apple Silicon MacBook을 개발 및 관리 환경으로 사용하고, 실제 OpenStack 실행 환경은 별도의 amd64 Ubuntu Server에서 구성한다.

---

## 2. 설치 환경

## 2.1 개발 및 관리 환경

| 항목 | 내용 |
|---|---|
| 장비 | MacBook |
| CPU Architecture | arm64 |
| 역할 | 코드 작성, 문서화, GitHub 관리, SSH 접속 |
| 주요 도구 | VS Code, Git, SSH |

Apple Silicon MacBook에서는 OpenStack의 전체 기능, 특히 VM 생성 및 중첩 가상화 실습에 제약이 있을 수 있으므로 직접 OpenStack을 실행하지 않고 관리 환경으로 사용한다.

---

## 2.2 OpenStack 실행 환경

| 항목 | 내용 |
|---|---|
| 장비 | 별도 amd64 Ubuntu Server |
| OS | Ubuntu Server 24.04 LTS |
| CPU | Intel 또는 AMD 4 Core 이상 |
| Memory | 최소 16GB, 권장 32GB |
| Disk | 최소 100GB, 권장 256GB 이상 |
| Network | 인터넷 연결 가능 |
| 역할 | OpenStack 구축 및 VM 운영 |

---

## 3. 설치 방식 선택

OpenStack은 다양한 설치 방식이 존재한다.

| 설치 방식 | 설명 | 본 프로젝트 적용 여부 |
|---|---|---|
| Canonical OpenStack Sunbeam | Ubuntu 기반 OpenStack 설치 방식 | 사용 |
| DevStack | 개발 및 테스트용 OpenStack | 대안 |
| MicroStack | Snap 기반 경량 OpenStack | 대안 |
| 수동 설치 | 각 컴포넌트를 직접 설치 | 미사용 |

본 프로젝트에서는 Ubuntu Server 24.04 LTS 기반의 Canonical OpenStack Sunbeam 방식을 기본 설치 방법으로 사용한다.

---

## 4. 사전 준비

## 4.1 시스템 업데이트

```bash
sudo apt update
sudo apt upgrade -y
```

## 4.2 기본 패키지 설치

```bash
sudo apt install -y curl wget git vim net-tools openssh-server
```

## 4.3 SSH 서비스 확인

```bash
sudo systemctl status ssh
```

SSH가 실행 중이 아니면 다음 명령어를 실행한다.

```bash
sudo systemctl enable --now ssh
```

## 4.4 서버 IP 확인

```bash
ip a
```

MacBook에서 SSH 접속 테스트:

```bash
ssh <사용자명>@<서버IP>
```

예시:

```bash
ssh cloudadmin@192.168.0.10
```

---

## 5. CPU 가상화 지원 확인

OpenStack은 VM 생성을 위해 CPU 가상화 지원이 필요하다.

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
```

결과가 `1` 이상이면 가상화 기능이 활성화된 상태이다.

```text
1 이상: 가상화 지원 가능
0: 가상화 미지원 또는 BIOS/UEFI에서 비활성화 상태
```

결과가 `0`이면 BIOS/UEFI에서 Intel VT-x 또는 AMD-V를 활성화해야 한다.

---

## 6. Snap 설치 확인

Canonical OpenStack 설치를 위해 snap 환경을 확인한다.

```bash
snap version
```

snap이 없다면 설치한다.

```bash
sudo apt install -y snapd
sudo systemctl enable --now snapd
```

---

## 7. OpenStack Snap 설치

```bash
sudo snap install openstack
```

설치 확인:

```bash
snap list openstack
```

---

## 8. Node 준비 스크립트 실행

```bash
sunbeam prepare-node-script --bootstrap | bash -x
```

명령 실행 후 필요한 그룹 변경을 적용한다.

```bash
newgrp snap_daemon
```

---

## 9. OpenStack Cluster Bootstrap

단일 노드 환경에서 control, compute, storage 역할을 모두 수행하도록 구성한다.

```bash
sunbeam cluster bootstrap --accept-defaults --role control,compute,storage
```

이 단계는 시간이 오래 걸릴 수 있다.

---

## 10. OpenStack 기본 설정

```bash
sunbeam configure --accept-defaults --openrc demo-openrc
```

설정이 완료되면 `demo-openrc` 파일이 생성된다.

---

## 11. OpenStack CLI 환경 변수 적용

```bash
source demo-openrc
```

인증 확인:

```bash
openstack token issue
```

정상적으로 토큰 정보가 출력되면 CLI 인증이 성공한 것이다.

---

## 12. OpenStack 서비스 확인

```bash
openstack service list
```

서버 목록 확인:

```bash
openstack server list
```

네트워크 목록 확인:

```bash
openstack network list
```

이미지 목록 확인:

```bash
openstack image list
```

---

## 13. Horizon Dashboard 접속

Dashboard URL 확인:

```bash
sunbeam dashboard-url
```

출력된 URL을 브라우저에서 접속한다.

로그인 정보는 설치 과정에서 출력된 계정 정보를 사용한다.

---

## 14. 설치 성공 기준

다음 항목이 모두 확인되면 OpenStack 기본 설치가 완료된 것으로 판단한다.

- `openstack` snap 설치 완료
- `sunbeam cluster bootstrap` 성공
- `demo-openrc` 생성
- `openstack token issue` 성공
- `openstack service list` 출력 성공
- Horizon Dashboard 접속 성공

---

## 15. 설치 후 캡처할 화면

README 및 블로그에 사용할 화면을 캡처한다.

| 캡처 파일명 | 내용 |
|---|---|
| `screenshots/openstack-dashboard.png` | Horizon Dashboard 메인 화면 |
| `screenshots/openstack-services.png` | OpenStack 서비스 목록 |
| `screenshots/openstack-network-list.png` | 네트워크 목록 |
| `screenshots/openstack-server-list.png` | 서버 목록 |

---

## 16. 예상 오류 및 대응

## 16.1 가상화 플래그가 보이지 않는 경우

증상:

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
```

결과:

```text
0
```

원인:

- BIOS/UEFI에서 가상화 기능 비활성화
- VM 내부에서 Nested Virtualization 미지원
- ARM 기반 환경에서 amd64 기준 실습 진행

대응:

- BIOS/UEFI에서 Intel VT-x 또는 AMD-V 활성화
- 물리 amd64 서버에서 설치
- 클라우드 VM 환경에서는 Nested Virtualization 지원 여부 확인

---

## 16.2 Snap 설치 실패

증상:

```text
error: cannot communicate with server
```

대응:

```bash
sudo systemctl restart snapd
sudo systemctl status snapd
```

필요 시 재설치:

```bash
sudo apt remove --purge snapd -y
sudo apt install -y snapd
```

---

## 16.3 Bootstrap 실패

증상:

```text
sunbeam cluster bootstrap failed
```

확인 항목:

```bash
free -h
df -h
ip a
sudo journalctl -xe
```

주요 원인:

- 메모리 부족
- 디스크 용량 부족
- 네트워크 설정 문제
- 가상화 미지원

---

## 17. 다음 단계

OpenStack 설치가 완료되면 다음 단계로 VM, Network, Storage, User 관리 실습을 진행한다.

다음 문서:

```text
docs/openstack-resource-management.md
```
