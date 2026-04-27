from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from _common import PROJECT_DIR


REPORT_DIR = PROJECT_DIR / "reports" / "security"
SONAR_RAW_FILE = REPORT_DIR / "sonar_issues.json"
SONAR_STATUS_FILE = REPORT_DIR / "sonar_export_status.json"
SNYK_RAW_FILE = REPORT_DIR / "snyk_issues.json"
SNYK_STATUS_FILE = REPORT_DIR / "snyk_export_status.json"
SYNTHESIS_FILE = REPORT_DIR / "rapport_sonar_snyk.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def map_sonar_to_level(severity: str) -> str:
    s = (severity or "").upper()
    if s in {"BLOCKER", "CRITICAL"}:
        return "critique"
    if s == "MAJOR":
        return "modere"
    return "faible"


def map_snyk_to_level(severity: str) -> str:
    s = (severity or "").lower()
    if s in {"high", "critical"}:
        return "critique"
    if s == "medium":
        return "modere"
    return "faible"


def empty_levels() -> dict[str, int]:
    return {"faible": 0, "modere": 0, "critique": 0}


def export_sonar(host_url: str, project_key: str, token: str | None) -> dict[str, Any]:
    if not token:
        raw = {
            "source": "sonarqube",
            "host_url": host_url,
            "project_key": project_key,
            "generated_at": now_iso(),
            "total": 0,
            "issues": [],
        }
        SONAR_RAW_FILE.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        status = {
            "ok": False,
            "source": "sonarqube",
            "reason": "SONAR_TOKEN manquant",
            "generated_at": now_iso(),
        }
        SONAR_STATUS_FILE.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return {"status": status, "levels": empty_levels(), "raw": raw}

    issues: list[dict[str, Any]] = []
    page = 1
    page_size = 500

    while True:
        response = requests.get(
            f"{host_url.rstrip('/')}/api/issues/search",
            params={
                "componentKeys": project_key,
                "types": "BUG,VULNERABILITY,CODE_SMELL",
                "statuses": "OPEN,CONFIRMED,REOPENED",
                "ps": page_size,
                "p": page,
            },
            auth=(token, ""),
            timeout=30,
        )

        if response.status_code >= 400:
            raw = {
                "source": "sonarqube",
                "host_url": host_url,
                "project_key": project_key,
                "generated_at": now_iso(),
                "total": 0,
                "issues": [],
            }
            SONAR_RAW_FILE.write_text(json.dumps(raw, indent=2), encoding="utf-8")
            status = {
                "ok": False,
                "source": "sonarqube",
                "reason": f"HTTP {response.status_code}",
                "generated_at": now_iso(),
            }
            SONAR_STATUS_FILE.write_text(json.dumps(status, indent=2), encoding="utf-8")
            return {"status": status, "levels": empty_levels(), "raw": raw}

        payload = response.json()
        issues.extend(payload.get("issues", []))
        paging = payload.get("paging", {})
        total = int(paging.get("total", 0))
        if len(issues) >= total or not payload.get("issues"):
            break
        page += 1

    raw = {
        "source": "sonarqube",
        "host_url": host_url,
        "project_key": project_key,
        "generated_at": now_iso(),
        "total": len(issues),
        "issues": issues,
    }
    SONAR_RAW_FILE.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    levels = empty_levels()
    for issue in issues:
        levels[map_sonar_to_level(issue.get("severity", ""))] += 1

    status = {
        "ok": True,
        "source": "sonarqube",
        "generated_at": now_iso(),
        "issue_count": len(issues),
    }
    SONAR_STATUS_FILE.write_text(json.dumps(status, indent=2), encoding="utf-8")
    return {"status": status, "levels": levels, "raw": raw}


def export_snyk() -> dict[str, Any]:
    if not os.getenv("SNYK_TOKEN"):
        raw = {
            "source": "snyk",
            "generated_at": now_iso(),
            "vulnerabilities": [],
        }
        SNYK_RAW_FILE.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        status = {
            "ok": False,
            "source": "snyk",
            "reason": "SNYK_TOKEN manquant",
            "generated_at": now_iso(),
        }
        SNYK_STATUS_FILE.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return {"status": status, "levels": empty_levels(), "raw": raw}

    if shutil.which("snyk") is None:
        raw = {
            "source": "snyk",
            "generated_at": now_iso(),
            "vulnerabilities": [],
        }
        SNYK_RAW_FILE.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        status = {
            "ok": False,
            "source": "snyk",
            "reason": "CLI snyk introuvable dans PATH",
            "generated_at": now_iso(),
        }
        SNYK_STATUS_FILE.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return {"status": status, "levels": empty_levels(), "raw": raw}

    cmd = [
        "snyk",
        "test",
        "--file=requirements.txt",
        "--package-manager=pip",
        f"--json-file-output={SNYK_RAW_FILE}",
    ]
    result = subprocess.run(cmd, cwd=str(PROJECT_DIR), check=False, text=True, capture_output=True)

    if not SNYK_RAW_FILE.exists():
        raw = {
            "source": "snyk",
            "generated_at": now_iso(),
            "vulnerabilities": [],
        }
        SNYK_RAW_FILE.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        status = {
            "ok": False,
            "source": "snyk",
            "reason": "Aucun export JSON produit",
            "generated_at": now_iso(),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
        SNYK_STATUS_FILE.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return {"status": status, "levels": empty_levels(), "raw": raw}

    raw = json.loads(SNYK_RAW_FILE.read_text(encoding="utf-8"))
    vulnerabilities = raw.get("vulnerabilities", [])

    levels = empty_levels()
    for vuln in vulnerabilities:
        levels[map_snyk_to_level(vuln.get("severity", ""))] += 1

    status = {
        "ok": True,
        "source": "snyk",
        "generated_at": now_iso(),
        "issue_count": len(vulnerabilities),
        "exit_code": result.returncode,
    }
    SNYK_STATUS_FILE.write_text(json.dumps(status, indent=2), encoding="utf-8")
    return {"status": status, "levels": levels, "raw": raw}


def synthesis_level(levels: dict[str, int]) -> str:
    if levels["critique"] > 0:
        return "critique"
    if levels["modere"] > 0:
        return "modere"
    return "faible"


def write_markdown_synthesis(sonar: dict[str, Any], snyk: dict[str, Any]) -> None:
    sonar_levels = sonar["levels"]
    snyk_levels = snyk["levels"]
    total_levels = {
        "faible": sonar_levels["faible"] + snyk_levels["faible"],
        "modere": sonar_levels["modere"] + snyk_levels["modere"],
        "critique": sonar_levels["critique"] + snyk_levels["critique"],
    }

    sonar_label = synthesis_level(sonar_levels)
    snyk_label = synthesis_level(snyk_levels)
    global_label = synthesis_level(total_levels)

    lines = [
        "# Rapport SonarQube + Snyk",
        "",
        f"Date generation (UTC): {now_iso()}",
        "",
        "## Export SonarQube",
        f"- Statut export: {'OK' if sonar['status']['ok'] else 'NON DISPONIBLE'}",
        f"- Interpretation: {sonar_label}",
        f"- Faible: {sonar_levels['faible']}",
        f"- Modere: {sonar_levels['modere']}",
        f"- Critique: {sonar_levels['critique']}",
        "",
        "## Export Snyk",
        f"- Statut export: {'OK' if snyk['status']['ok'] else 'NON DISPONIBLE'}",
        f"- Interpretation: {snyk_label}",
        f"- Faible: {snyk_levels['faible']}",
        f"- Modere: {snyk_levels['modere']}",
        f"- Critique: {snyk_levels['critique']}",
        "",
        "## Synthese globale",
        f"- Niveau global: {global_label}",
        f"- Faible: {total_levels['faible']}",
        f"- Modere: {total_levels['modere']}",
        f"- Critique: {total_levels['critique']}",
        "",
        "## Artefacts",
        "- sonar_issues.json",
        "- sonar_export_status.json",
        "- snyk_issues.json",
        "- snyk_export_status.json",
        "- rapport_sonar_snyk.md",
    ]

    SYNTHESIS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export SonarQube/Snyk issues and produce synthetic interpretation."
    )
    parser.add_argument(
        "--sonar-host-url",
        default=os.getenv("SONAR_HOST_URL", "https://sonarcloud.io"),
        help="SonarQube/SonarCloud URL.",
    )
    parser.add_argument(
        "--sonar-project-key",
        default=os.getenv("SONAR_PROJECT_KEY", "RobelManoa_urbanhub-ms-alerte"),
        help="Sonar project key.",
    )
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    sonar = export_sonar(
        host_url=args.sonar_host_url,
        project_key=args.sonar_project_key,
        token=os.getenv("SONAR_TOKEN"),
    )
    snyk = export_snyk()

    write_markdown_synthesis(sonar, snyk)

    print(f"Reports generated in: {REPORT_DIR}")
    print(f"Synthesis: {SYNTHESIS_FILE}")

    if not sonar["status"]["ok"] or not snyk["status"]["ok"]:
        print("Warning: one or more exports are not available. Check *_export_status.json.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
