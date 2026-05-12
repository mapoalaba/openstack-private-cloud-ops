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

    filename = f"incident-{filename_timestamp}-{server_name}.md"
    report_path = os.path.join(report_dir, filename)

    content = f"""# Incident Report - {server_name}

## 1. 장애 개요

| 항목 | 내용 |
|---|---|
| 발생 시간 | {timestamp} |
| 대상 서버 | {server_name} |
| 장애 유형 | {incident_type} |
| 감지 상태 | {detected_status} |
| 복구 작업 | {recovery_action} |
| 복구 결과 | {recovery_result} |

---

## 2. 장애 감지 내용

`{server_name}` 서버의 상태가 정상 기준과 다르게 감지되었다.

- 정상 기준: `ACTIVE`
- 감지 상태: `{detected_status}`

---

## 3. 복구 절차

수행한 복구 작업:

```text
{recovery_action}