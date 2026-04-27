from __future__ import annotations

import argparse
import sys

from _common import PROJECT_DIR, REPO_ROOT, run_cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build script for ms-alerte-usager (dependencies and optional Docker image)."
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Install development dependencies (requirements-dev.txt).",
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Build Docker image for the service.",
    )
    args = parser.parse_args()

    run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], cwd=PROJECT_DIR)

    install_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    if args.dev:
        install_cmd.extend(["-r", "requirements-dev.txt"])
    run_cmd(install_cmd, cwd=PROJECT_DIR)

    if args.docker:
        run_cmd(["docker", "compose", "build", "ms-alerte-usager"], cwd=REPO_ROOT)

    print("Build completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
