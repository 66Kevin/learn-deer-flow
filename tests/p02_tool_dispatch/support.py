from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
P02_ROOT = REPO_ROOT / "P02-tool-dispatch"
P02_BACKEND_ROOT = P02_ROOT / "backend"
P02_HARNESS_ROOT = P02_BACKEND_ROOT / "packages" / "harness"


def ensure_p02_harness_on_path() -> None:
    harness_path = str(P02_HARNESS_ROOT)
    if harness_path not in sys.path:
        sys.path.insert(0, harness_path)
