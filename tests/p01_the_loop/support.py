from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
P01_ROOT = REPO_ROOT / "P01-the-loop"
P01_BACKEND_ROOT = P01_ROOT / "backend"
P01_HARNESS_ROOT = P01_BACKEND_ROOT / "packages" / "harness"


def ensure_p01_harness_on_path() -> None:
    harness_path = str(P01_HARNESS_ROOT)
    if harness_path not in sys.path:
        sys.path.insert(0, harness_path)

