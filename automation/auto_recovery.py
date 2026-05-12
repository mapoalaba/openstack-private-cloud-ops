import os
import sys
import time
from datetime import datetime
from typing import Dict

import yaml

from openstack_client import OpenStackClient, OpenStackCommandError
from incident_report import create_incident_report


def load_config(config_path: str) -> Dict:
    """YAML 설정 파일을 읽어옵니다."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def ensure_log_dir(log_path: str) -> None:
    """로그 디렉터리를 생성합니다."""
    log_dir = os.path.dirname(log_path)

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)


def write_log(log_path: str, message: str) -> None:
    """콘솔과 로그 파일에 메시지를 기록합니다."""
    ensure_log_dir(log_path)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"

    print(line)

    with open(log_path, "a", encoding="utf-8") as file:
        file.write(line + "\n")


def get_server_status(client: OpenStackClient, server_name: str) -> str:
    """특정 VM의 현재 상태를 반환합니다."""
    server = client.get_server(server_name)
    return server.get("status") or server.get("Status") or "UNKNOWN"


def wait_until_active(
    client: OpenStackClient,
    server_name: str,
    expected_status: str,
    wait_seconds: int,
    max_retry: int,
    log_path: str,
) -> bool:
    """
    VM이 expected_status 상태가 될 때까지 대기합니다.
    """
    for attempt in range(1, max_retry + 1):
        time.sleep(wait_seconds)

        current_status = get_server_status(client, server_name)
        write_log(
            log_path,
            f"[CHECK] {server_name} status check {attempt}/{max_retry}: {current_status}",
        )

        if current_status == expected_status:
            return True

    return False


def recover_vm(config_path: str, server_name: str, detected_status: str) -> int:
    """
    비정상 VM을 복구합니다.

    반환값:
    - 0: 복구 성공
    - 1: 복구 실패
    - 2: 설정상 복구 비활성화
    - 3: OpenStack 명령 오류
    """
    config = load_config(config_path)

    openrc_path = config["openstack"]["openrc_path"]
    expected_status = config["health_check"]["expected_status"]
    recovery_enabled = config["recovery"]["enabled"]
    wait_seconds = config["recovery"]["wait_seconds"]
    max_retry = config["recovery"]["max_retry"]
    log_path = config["log"]["recovery_path"]
    report_dir = config["report"]["path"]

    if not recovery_enabled:
        write_log(log_path, f"[SKIP] Recovery disabled. Target: {server_name}")
        return 2

    client = OpenStackClient(openrc_path=openrc_path)

    write_log(
        log_path,
        f"[START] Recovery started. Target: {server_name}, detected_status: {detected_status}",
    )

    try:
        if detected_status == "SHUTOFF":
            recovery_action = f"openstack server start {server_name}"
            write_log(log_path, f"[ACTION] {recovery_action}")
            client.start_server(server_name)

        elif detected_status == "ERROR":
            recovery_action = f"manual check required for {server_name}"
            recovery_result = "ERROR 상태는 자동 시작 대신 수동 점검 대상으로 분류함"
            write_log(log_path, f"[MANUAL_REQUIRED] {server_name} is ERROR state")

            report_path = create_incident_report(
                report_dir=report_dir,
                server_name=server_name,
                incident_type="VM ERROR",
                detected_status=detected_status,
                recovery_action=recovery_action,
                recovery_result=recovery_result,
                detail="OpenStack VM status is ERROR. Check nova-compute logs and instance details.",
            )

            write_log(log_path, f"[REPORT] Created: {report_path}")
            return 1

        else:
            recovery_action = f"status check only for {server_name}"
            recovery_result = f"Unsupported recovery status: {detected_status}"
            write_log(
                log_path,
                f"[UNSUPPORTED] {server_name} status {detected_status} is not auto-recoverable",
            )

            report_path = create_incident_report(
                report_dir=report_dir,
                server_name=server_name,
                incident_type="Unsupported VM Status",
                detected_status=detected_status,
                recovery_action=recovery_action,
                recovery_result=recovery_result,
            )

            write_log(log_path, f"[REPORT] Created: {report_path}")
            return 1

        recovered = wait_until_active(
            client=client,
            server_name=server_name,
            expected_status=expected_status,
            wait_seconds=wait_seconds,
            max_retry=max_retry,
            log_path=log_path,
        )

        if recovered:
            recovery_result = f"{server_name} recovered to {expected_status}"
            write_log(log_path, f"[SUCCESS] {recovery_result}")

            report_path = create_incident_report(
                report_dir=report_dir,
                server_name=server_name,
                incident_type="VM SHUTOFF",
                detected_status=detected_status,
                recovery_action=recovery_action,
                recovery_result=recovery_result,
            )

            write_log(log_path, f"[REPORT] Created: {report_path}")
            return 0

        recovery_result = f"{server_name} recovery failed after {max_retry} checks"
        write_log(log_path, f"[FAILED] {recovery_result}")

        report_path = create_incident_report(
            report_dir=report_dir,
            server_name=server_name,
            incident_type="VM Recovery Failed",
            detected_status=detected_status,
            recovery_action=recovery_action,
            recovery_result=recovery_result,
        )

        write_log(log_path, f"[REPORT] Created: {report_path}")
        return 1

    except OpenStackCommandError as error:
        write_log(log_path, f"[ERROR] OpenStack command failed: {error}")

        create_incident_report(
            report_dir=report_dir,
            server_name=server_name,
            incident_type="OpenStack Command Error",
            detected_status=detected_status,
            recovery_action="OpenStack CLI command execution",
            recovery_result="Recovery failed due to OpenStack command error",
            detail=str(error),
        )

        return 3


if __name__ == "__main__":
    default_config_path = os.path.join(
        os.path.dirname(__file__),
        "config.yaml"
    )

    if len(sys.argv) < 3:
        print("Usage: python automation/auto_recovery.py <server_name> <detected_status> [config_path]")
        print("Example: python automation/auto_recovery.py test-01 SHUTOFF")
        sys.exit(1)

    server_name_arg = sys.argv[1]
    detected_status_arg = sys.argv[2]
    config_path_arg = sys.argv[3] if len(sys.argv) >= 4 else default_config_path

    exit_code = recover_vm(
        config_path=config_path_arg,
        server_name=server_name_arg,
        detected_status=detected_status_arg,
    )

    sys.exit(exit_code)