from __future__ import annotations

import argparse
import sys

from _common import PROJECT_DIR, run_cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run quality checks for ms-alerte-usager."
    )
    parser.add_argument(
        "--skip-lint",
        action="store_true",
        help="Skip flake8 linting.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest execution.",
    )
    args = parser.parse_args()

    run_cmd([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-r", "requirements-dev.txt"], cwd=PROJECT_DIR)

    if not args.skip_tests:
        run_cmd(
            [
                sys.executable,
                "-m",
                "pytest",
                "test/unit",
                "--junitxml=report_tests.xml",
                "--cov=src",
                "--cov-report=xml:coverage.xml",
                "--cov-report=term-missing",
                "--cov-fail-under=80",
            ],
            cwd=PROJECT_DIR,
        )

    if not args.skip_lint:
        run_cmd(
            [
                sys.executable,
                "-m",
                "flake8",
                "src",
                "test",
                "--config=.flake8",
                "--output-file=flake8-report.txt",
            ],
            cwd=PROJECT_DIR,
        )

    print("Quality checks completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
