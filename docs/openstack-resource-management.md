# OpenStack Resource Management 문서

## 1. 문서 목적

본 문서는 `OpenStack 기반 Private Cloud 운영 자동화 및 장애 대응 시스템` 프로젝트에서 OpenStack의 핵심 리소스인 VM, Network, Storage, User/Project/Role을 관리하는 절차를 정리한 문서이다.

OpenStack 구축 이후 실제 클라우드 운영자가 수행하는 기본 운영 작업을 실습하고, 이후 모니터링 및 장애 대응 자동화의 기반 환경을 구성하는 것을 목표로 한다.

---

## 2. 관리 대상 리소스

본 프로젝트에서 관리할 OpenStack 리소스는 다음과 같다.

| 구분 | OpenStack 서비스 | 관리 대상 |
|---|---|---|
| VM | Nova | Instance 생성, 중지, 삭제, 상태 확인 |
| Network | Neutron | Network, Subnet, Router, Floating IP, Security Group |
| Storage | Glance, Cinder | Image, Volume 생성 및 연결 |
| User | Keystone | Project, User, Role 관리 |

---

## 3. 사전 조건

OpenStack 설치가 완료되어 있어야 한다.

확인 명령어:

```bash
source demo-openrc
openstack token issue
openstack service list
```

정상적으로 토큰과 서비스 목록이 출력되면 리소스 관리 실습을 진행할 수 있다.

---

## 4. VM 관리

## 4.1 이미지 목록 확인

VM 생성을 위해 사용할 이미지를 확인한다.

```bash
openstack image list
```

이미지가 없는 경우 Ubuntu Cloud Image를 등록한다.

```bash
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
```

```bash
openstack image create "ubuntu-24.04" \
  --file noble-server-cloudimg-amd64.img \
  --disk-format qcow2 \
  --container-format bare \
  --public
```

등록 확인:

```bash
openstack image list
```

---

## 4.2 Flavor 확인

Flavor는 VM의 CPU, Memory, Disk 크기를 정의한다.

```bash
openstack flavor list
```

필요 시 테스트용 Flavor를 생성한다.

```bash
openstack flavor create m1.small \
  --ram 2048 \
  --disk 20 \
  --vcpus 1
```

---

## 4.3 Key Pair 생성

VM에 SSH 접속하기 위한 Key Pair를 생성한다.

```bash
openstack keypair create lab-key > lab-key.pem
chmod 600 lab-key.pem
```

Key Pair 확인:

```bash
openstack keypair list
```

---

## 4.4 VM 생성

기본 VM을 생성한다.

```bash
openstack server create web-01 \
  --image ubuntu-24.04 \
  --flavor m1.small \
  --key-name lab-key \
  --network private-network
```

VM 목록 확인:

```bash
openstack server list
```

VM 상세 확인:

```bash
openstack server show web-01
```

---

## 4.5 VM 상태 관리

VM 중지:

```bash
openstack server stop web-01
```

VM 시작:

```bash
openstack server start web-01
```

VM 재부팅:

```bash
openstack server reboot web-01
```

VM 삭제:

```bash
openstack server delete web-01
```

---

## 4.6 본 프로젝트에서 사용할 VM 구성

| VM 이름 | 역할 | 설치 예정 서비스 |
|---|---|---|
| web-01 | 웹 서버 | Nginx, Node Exporter |
| db-01 | DB 테스트 서버 | MySQL 또는 MariaDB, Node Exporter |
| monitor-01 | 모니터링 서버 | Prometheus, Grafana |
| test-01 | 장애 테스트 서버 | stress, Node Exporter |

---

## 5. Network 관리

## 5.1 네트워크 구성 목표

본 프로젝트의 기본 네트워크 구조는 다음과 같다.

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

---

## 5.2 Private Network 생성

```bash
openstack network create private-network
```

확인:

```bash
openstack network list
```

---

## 5.3 Subnet 생성

```bash
openstack subnet create private-subnet \
  --network private-network \
  --subnet-range 10.0.0.0/24 \
  --gateway 10.0.0.1 \
  --dns-nameserver 8.8.8.8
```

확인:

```bash
openstack subnet list
```

---

## 5.4 Router 생성

```bash
openstack router create lab-router
```

Subnet을 Router에 연결한다.

```bash
openstack router add subnet lab-router private-subnet
```

Router 확인:

```bash
openstack router list
```

---

## 5.5 External Network 연결

External Network 목록을 확인한다.

```bash
openstack network list --external
```

External Network를 Router Gateway로 설정한다.

```bash
openstack router set lab-router --external-gateway external
```

`external` 이름은 실제 환경의 External Network 이름에 맞게 수정해야 한다.

---

## 5.6 Security Group 설정

기본 Security Group을 확인한다.

```bash
openstack security group list
```

SSH 허용:

```bash
openstack security group rule create \
  --proto tcp \
  --dst-port 22 \
  default
```

HTTP 허용:

```bash
openstack security group rule create \
  --proto tcp \
  --dst-port 80 \
  default
```

ICMP 허용:

```bash
openstack security group rule create \
  --proto icmp \
  default
```

Node Exporter 포트 허용:

```bash
openstack security group rule create \
  --proto tcp \
  --dst-port 9100 \
  default
```

Prometheus 포트 허용:

```bash
openstack security group rule create \
  --proto tcp \
  --dst-port 9090 \
  default
```

Grafana 포트 허용:

```bash
openstack security group rule create \
  --proto tcp \
  --dst-port 3000 \
  default
```

---

## 5.7 Floating IP 생성 및 연결

Floating IP 생성:

```bash
openstack floating ip create external
```

Floating IP 목록 확인:

```bash
openstack floating ip list
```

VM에 Floating IP 연결:

```bash
openstack server add floating ip web-01 <FLOATING_IP>
```

접속 테스트:

```bash
ping <FLOATING_IP>
ssh -i lab-key.pem ubuntu@<FLOATING_IP>
```

---

## 6. Storage 관리

## 6.1 Volume 목록 확인

```bash
openstack volume list
```

---

## 6.2 Volume 생성

```bash
openstack volume create web-data-volume --size 5
```

Volume 확인:

```bash
openstack volume list
```

---

## 6.3 VM에 Volume 연결

```bash
openstack server add volume web-01 web-data-volume
```

VM 내부에서 디스크 확인:

```bash
lsblk
```

예상 출력:

```text
vdb      252:16   0   5G  0 disk
```

---

## 6.4 파일 시스템 생성

VM 내부에서 실행한다.

```bash
sudo mkfs.ext4 /dev/vdb
```

마운트 디렉터리 생성:

```bash
sudo mkdir -p /data
```

마운트:

```bash
sudo mount /dev/vdb /data
```

확인:

```bash
df -h
```

---

## 6.5 테스트 파일 생성

```bash
echo "OpenStack Cinder Volume Test" | sudo tee /data/test.txt
cat /data/test.txt
```

---

## 6.6 Volume 분리 및 재연결 테스트

VM에서 마운트 해제:

```bash
sudo umount /data
```

OpenStack에서 Volume 분리:

```bash
openstack server remove volume web-01 web-data-volume
```

다른 VM에 연결:

```bash
openstack server add volume test-01 web-data-volume
```

이후 `/data/test.txt` 파일이 유지되는지 확인한다.

---

## 7. User / Project / Role 관리

## 7.1 Project 생성

```bash
openstack project create ops-project
openstack project create dev-project
openstack project create test-project
```

확인:

```bash
openstack project list
```

---

## 7.2 User 생성

```bash
openstack user create ops-admin --password 'ChangeMe123!'
openstack user create dev-user --password 'ChangeMe123!'
openstack user create readonly-user --password 'ChangeMe123!'
```

확인:

```bash
openstack user list
```

---

## 7.3 Role 확인

```bash
openstack role list
```

---

## 7.4 Role 부여

운영자 계정에 admin 역할 부여:

```bash
openstack role add \
  --project ops-project \
  --user ops-admin \
  admin
```

개발자 계정에 member 역할 부여:

```bash
openstack role add \
  --project dev-project \
  --user dev-user \
  member
```

조회 전용 계정에 reader 역할 부여:

```bash
openstack role add \
  --project test-project \
  --user readonly-user \
  reader
```

Role 부여 확인:

```bash
openstack role assignment list --names
```

---

## 7.5 권한 테스트

각 사용자별 openrc 파일을 생성하거나 Horizon Dashboard에서 로그인하여 권한 차이를 확인한다.

확인 항목:

| 사용자 | 예상 권한 |
|---|---|
| ops-admin | 리소스 생성, 수정, 삭제 가능 |
| dev-user | 프로젝트 내 리소스 생성 가능 |
| readonly-user | 리소스 조회 중심 |

---

## 8. 운영 확인 명령어 모음

## 8.1 VM 확인

```bash
openstack server list
openstack server show web-01
```

## 8.2 Network 확인

```bash
openstack network list
openstack subnet list
openstack router list
openstack floating ip list
```

## 8.3 Security Group 확인

```bash
openstack security group list
openstack security group rule list default
```

## 8.4 Storage 확인

```bash
openstack volume list
openstack volume show web-data-volume
```

## 8.5 User 확인

```bash
openstack project list
openstack user list
openstack role assignment list --names
```

---

## 9. README에 사용할 캡처 목록

| 파일명 | 캡처 내용 |
|---|---|
| `screenshots/vm-list.png` | VM Instance 목록 |
| `screenshots/network-topology.png` | Network Topology |
| `screenshots/volume-list.png` | Volume 목록 |
| `screenshots/user-role-list.png` | User / Project / Role 목록 |
| `screenshots/floating-ip-list.png` | Floating IP 목록 |
| `screenshots/security-group-rules.png` | Security Group 규칙 |

---

## 10. 예상 오류 및 해결 방향

## 10.1 VM 생성 실패

증상:

```text
No valid host was found
```

가능한 원인:

- Compute 리소스 부족
- Flavor가 너무 큼
- 이미지 문제
- Nova 서비스 문제

확인 명령어:

```bash
openstack compute service list
openstack hypervisor list
openstack server show <VM_NAME>
```

---

## 10.2 SSH 접속 실패

증상:

```text
ssh: connect to host <IP> port 22: Operation timed out
```

가능한 원인:

- Floating IP 미연결
- Security Group 22번 포트 미허용
- VM 내부 SSH 서비스 미실행
- Router 또는 External Network 설정 오류

확인 명령어:

```bash
openstack floating ip list
openstack security group rule list default
openstack router list
ping <FLOATING_IP>
```

---

## 10.3 HTTP 접속 실패

증상:

```text
curl: Failed to connect
```

가능한 원인:

- Nginx 미설치 또는 미실행
- Security Group 80번 포트 미허용
- Floating IP 문제

확인 명령어:

```bash
sudo systemctl status nginx
openstack security group rule list default
curl http://<FLOATING_IP>
```

---

## 10.4 Volume 연결 실패

증상:

```text
Volume status is not available
```

가능한 원인:

- Volume 상태가 available이 아님
- 이미 다른 VM에 연결되어 있음
- Cinder 서비스 문제

확인 명령어:

```bash
openstack volume list
openstack volume show <VOLUME_NAME>
openstack volume service list
```

---

## 11. 완료 기준

다음 항목이 모두 완료되면 Resource Management 단계가 완료된 것으로 판단한다.

- Ubuntu 이미지 등록 완료
- Flavor 생성 또는 확인 완료
- Key Pair 생성 완료
- VM 4개 생성 완료
- Private Network / Subnet / Router 구성 완료
- Floating IP 연결 완료
- Security Group 규칙 설정 완료
- Volume 생성 및 VM 연결 완료
- Project / User / Role 생성 완료
- 사용자별 권한 테스트 완료
- 주요 화면 캡처 완료

---

## 12. 다음 단계

다음 단계에서는 Prometheus와 Grafana를 활용해 OpenStack VM 및 서버 상태를 모니터링하는 환경을 구성한다.

다음 문서:

```text
docs/monitoring-guide.md
```