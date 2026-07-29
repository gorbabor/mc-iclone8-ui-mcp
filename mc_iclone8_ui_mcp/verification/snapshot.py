from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def file_fingerprint(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {"exists": False, "path": str(target)}
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return {"exists": True, "path": str(target), "size": target.stat().st_size, "sha256": digest}


def compare_visible_state(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changed = sorted({*before.keys(), *after.keys()} - {"timestamp"})
    differences = {key: {"before": before.get(key), "after": after.get(key)} for key in changed if before.get(key) != after.get(key)}
    return {"changed": bool(differences), "differences": differences}
