import os
import sys
from datetime import datetime
from typing import Dict, List

import yaml

from openstack_client import OpenStackClient, OpenStackCommandError


def load_config(config_path: str) -> Dict:
    """YAML 설정 파일을 읽어옵니다."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def ensure_log_dir(log_path: str) -> None:
    """로그 파일이 저장될 디렉터리를 생성합니다."""
    log_dir = os.path.dirname(log_path)

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)


def write_log(log_path: str, message: str) -> None:
    """로그 파일에 메시지를 기록합니다."""
    ensure_log_dir(log_path)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"

    print(line)

    with open(log_path, "a", encoding="utf-8") as file:
        file.write(line + "\n")


def normalize_server_list(raw_servers: List[Dict]) -> Dict[str, Dict]:
    """
    OpenStack CLI 결과를 VM 이름 기준 dictionary로 변환합니다.
    """
    servers = {}

    for server in raw_servers:
        name = server.get("Name")
        if name:
            servers[name] = server

    return servers


def check_vm_health(config_path: str) -> int:
    """
    VM 상태를 점검합니다.

    반환값:
    - 0: 모든 VM 정상
    - 1: 하나 이상의 VM 비정상
    - 2: OpenStack CLI 실행 오류
    """
    config = load_config(config_path)

    openrc_path = config["openstack"]["openrc_path"]
    expected_status = config["health_check"]["expected_status"]
    target_servers = config["health_check"]["target_servers"]
    log_path = config["log"]["path"]

    client = OpenStackClient(openrc_path=openrc_path)

    try:
        raw_servers = client.list_servers()
    except OpenStackCommandError as error:
        write_log(log_path, f"[ERROR] OpenStack command failed: {error}")
        return 2

    servers = normalize_server_list(raw_servers)

    has_error = False

    write_log(log_path, "Starting VM health check")

    for target in target_servers:
        server = servers.get(target)

        if not server:
            has_error = True
            write_log(log_path, f"[CRITICAL] {target} not found")
            continue

        status = server.get("Status", "UNKNOWN")

        if status == expected_status:
            write_log(log_path, f"[OK] {target} status: {status}")
        else:
            has_error = True
            write_log(
                log_path,
                f"[WARN] {target} status: {status}, expected: {expected_status}"
            )
            write_log(
                log_path,
                f"[ACTION_REQUIRED] {target} needs recovery"
            )

    write_log(log_path, "Finished VM health check")

    return 1 if has_error else 0


if __name__ == "__main__":
    default_config_path = os.path.join(
        os.path.dirname(__file__),
        "config.yaml"
    )

    config_path = sys.argv[1] if len(sys.argv) > 1 else default_config_path
    exit_code = check_vm_health(config_path)

    sys.exit(exit_code)