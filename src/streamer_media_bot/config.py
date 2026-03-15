from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PACKAGE_ROOT / "config" / "config.json"


def load_config(path: Path | None = None) -> dict[str, Any]:
    target = path or CONFIG_PATH
    with target.open("r", encoding="utf-8") as f:
        return json.load(f)


def project_root() -> Path:
    return PACKAGE_ROOT
