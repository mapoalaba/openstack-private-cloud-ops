import json
import subprocess
from typing import Any, Dict, List


class OpenStackCommandError(Exception):
    """OpenStack CLI 실행 중 오류가 발생했을 때 사용하는 예외입니다."""
    pass


class OpenStackClient:
    """
    OpenStack CLI를 Python에서 호출하기 위한 간단한 클라이언트입니다.

    이 프로젝트에서는 OpenStack SDK 대신 CLI 기반으로 먼저 구현합니다.
    이유:
    - 설치와 인증 흐름이 단순함
    - openrc 파일을 그대로 활용 가능
    - 포트폴리오에서 동작 흐름을 설명하기 쉬움
    """

    def __init__(self, openrc_path: str):
        self.openrc_path = openrc_path

    def _run_openstack_command(self, command: str) -> str:
        """
        openrc 파일을 source 한 뒤 OpenStack CLI 명령어를 실행합니다.
        """
        shell_command = f"source {self.openrc_path} && {command}"

        result = subprocess.run(
            shell_command,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise OpenStackCommandError(
                f"Command failed: {command}\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

        return result.stdout.strip()

    def list_servers(self) -> List[Dict[str, Any]]:
        """
        OpenStack VM 목록을 JSON 형태로 조회합니다.
        """
        output = self._run_openstack_command(
            "openstack server list -f json"
        )

        if not output:
            return []

        return json.loads(output)

    def get_server(self, server_name: str) -> Dict[str, Any]:
        """
        특정 VM의 상세 정보를 JSON 형태로 조회합니다.
        """
        output = self._run_openstack_command(
            f"openstack server show {server_name} -f json"
        )

        if not output:
            return {}

        return json.loads(output)

    def start_server(self, server_name: str) -> None:
        """
        특정 VM을 시작합니다.
        자동 복구 단계에서 사용합니다.
        """
        self._run_openstack_command(
            f"openstack server start {server_name}"
        )

    def stop_server(self, server_name: str) -> None:
        """
        테스트용으로 특정 VM을 중지할 때 사용합니다.
        """
        self._run_openstack_command(
            f"openstack server stop {server_name}"
        )