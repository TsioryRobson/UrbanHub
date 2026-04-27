from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _common import PROJECT_DIR, run_cmd


def main() -> int:
    report_txt = PROJECT_DIR / "rapport_tests.txt"
    junit_xml = PROJECT_DIR / "rapport_tests.xml"
    coverage_html = PROJECT_DIR / "coverage_html"

    run_cmd(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
            "-r",
            "requirements-dev.txt",
        ],
        cwd=PROJECT_DIR,
    )

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "test/unit",
        "-v",
        f"--junitxml={junit_xml.name}",
        "--cov=src",
        f"--cov-report=html:{coverage_html.name}",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing",
    ]

    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_DIR),
        text=True,
        capture_output=True,
        check=False,
    )

    combined_output = result.stdout
    if result.stderr:
        combined_output += "\n[stderr]\n" + result.stderr

    report_txt.write_text(combined_output, encoding="utf-8")

    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    print(f"Test report: {report_txt}")
    print(f"JUnit report: {junit_xml}")
    print(f"Coverage HTML: {coverage_html}")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
