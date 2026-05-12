import os
from datetime import datetime
from typing import Optional


def ensure_dir(path: str) -> None:
    """디렉터리가 없으면 생성합니다."""
    os.makedirs(path, exist_ok=True)


def create_incident_report(
    report_dir: str,
    server_name: str,
    incident_type: str,
    detected_status: str,
    recovery_action: str,
    recovery_result: str,
    detail: Optional[str] = None,
) -> str:
    """
    장애 대응 결과를 Markdown 보고서로 생성합니다.
    """
    ensure_dir(report_dir)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    filename_timestamp = now.strftime("%Y%m%d-%H%M%S")

    safe_server_name = server_name.replace(" ", "-")
    filename = f"incident-{filename_timestamp}-{safe_server_name}.md"
    report_path = os.path.join(report_dir, filename)

    detail_text = detail if detail else "추가 상세 로그 없음"

    lines = [
        f"# Incident Report - {server_name}",
        "",
        "## 1. 장애 개요",
        "",
        "| 항목 | 내용 |",
        "|---|---|",
        f"| 발생 시간 | {timestamp} |",
        f"| 대상 서버 | {server_name} |",
        f"| 장애 유형 | {incident_type} |",
        f"| 감지 상태 | {detected_status} |",
        f"| 복구 작업 | {recovery_action} |",
        f"| 복구 결과 | {recovery_result} |",
        "",
        "---",
        "",
        "## 2. 장애 감지 내용",
        "",
        f"`{server_name}` 서버의 상태가 정상 기준과 다르게 감지되었다.",
        "",
        "- 정상 기준: `ACTIVE`",
        f"- 감지 상태: `{detected_status}`",
        "",
        "---",
        "",
        "## 3. 복구 절차",
        "",
        "수행한 복구 작업:",
        "",
        "```text",
        recovery_action,
        "```",
        "",
        "---",
        "",
        "## 4. 복구 결과",
        "",
        "```text",
        recovery_result,
        "```",
        "",
        "---",
        "",
        "## 5. 상세 로그",
        "",
        "```text",
        detail_text,
        "```",
        "",
        "---",
        "",
        "## 6. 재발 방지 방안",
        "",
        "- VM 상태를 주기적으로 점검한다.",
        "- SHUTOFF 또는 ERROR 상태 발생 시 즉시 알림을 발생시킨다.",
        "- 동일 장애가 반복되는 경우 Nova Compute 로그를 확인한다.",
        "- 인스턴스 리소스 부족, 이미지 오류, 호스트 장애 여부를 추가 점검한다.",
        "",
    ]

    content = "\n".join(lines)

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(content)

    return report_path