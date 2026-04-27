from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_DIR.parent


def run_cmd(command: Iterable[str], cwd: Path, *, check: bool = True) -> int:
    printable = " ".join(command)
    print(f"$ {printable}")
    result = subprocess.run(list(command), cwd=str(cwd), check=False)
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result.returncode
