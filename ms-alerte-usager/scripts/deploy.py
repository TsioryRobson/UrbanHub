from __future__ import annotations

import argparse

from _common import REPO_ROOT, run_cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deploy script for local Docker Compose environment."
    )
    parser.add_argument(
        "--down",
        action="store_true",
        help="Stop and remove containers instead of deploying.",
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Follow logs after deployment.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    args = parser.parse_args()

    commands: list[list[str]] = []
    if args.down:
        commands.append(["docker", "compose", "down"])
    else:
        commands.append(["docker", "compose", "up", "-d", "--build"])
        if args.logs:
            commands.append(["docker", "compose", "logs", "-f", "ms-alerte-usager"])

    for command in commands:
        if args.dry_run:
            print(f"$ {' '.join(command)}")
        else:
            run_cmd(command, cwd=REPO_ROOT)

    print("Deployment script completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
